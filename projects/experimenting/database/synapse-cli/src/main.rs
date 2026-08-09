//! SynapseDB command-line interface.
//!
//! Usage:
//!
//! ```text
//! synapse init --dir ./data --segments 100000
//! synapse write --dir ./data --entity 1 --attr name --value '"hello"' --ts 1
//! synapse read --dir ./data --offset 0
//! synapse snapshot --dir ./data --as-of 10
//! synapse verify --dir ./data
//! synapse recover --dir ./data
//! ```

use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;
use synapse_log::{recover, LocalLog};
use synapse_types::{Attribute, Diff, EntityId, LogPosition, Record, Timestamp, Value};

/// SynapseDB — a temporal differential entity store.
#[derive(Parser)]
#[command(name = "synapse")]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Create a new SynapseDB data directory.
    Init {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,

        /// Maximum records per segment.
        #[arg(short, long, default_value_t = 100_000)]
        segments: usize,
    },
    /// Append a record to the log.
    Write {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,

        /// Entity id as a 128-bit unsigned integer.
        #[arg(short, long, value_name = "ID")]
        entity: u128,

        /// Attribute name.
        #[arg(short, long, value_name = "NAME")]
        attr: String,

        /// Value as JSON (null, true, -42, 3.14, "text", or "0xdeadbeef" for bytes).
        #[arg(short, long, value_name = "JSON")]
        value: String,

        /// Timestamp (nanoseconds or logical clock).
        #[arg(short, long, value_name = "TS")]
        ts: u64,

        /// Differential sign.
        #[arg(short, long, value_enum, default_value = "added")]
        diff: DiffArg,
    },
    /// Read a record by its global offset.
    Read {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,

        /// Global offset.
        #[arg(short, long, value_name = "OFFSET")]
        offset: u64,
    },
    /// Print all records with timestamp <= as_of.
    Snapshot {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,

        /// Latest timestamp to include.
        #[arg(short, long, value_name = "TS")]
        as_of: u64,
    },
    /// Verify log integrity using the Merkle Mountain Range.
    Verify {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,
    },
    /// Recover the log after an unclean shutdown.
    Recover {
        /// Directory for segment files.
        #[arg(short, long, value_name = "DIR")]
        dir: PathBuf,
    },
}

#[derive(Copy, Clone, Debug, ValueEnum)]
enum DiffArg {
    Added,
    Retracted,
}

impl From<DiffArg> for Diff {
    fn from(arg: DiffArg) -> Self {
        match arg {
            DiffArg::Added => Diff::Added,
            DiffArg::Retracted => Diff::Retracted,
        }
    }
}

fn open_log(dir: &std::path::Path) -> Result<LocalLog> {
    let has_segments = std::fs::read_dir(dir)
        .ok()
        .map(|mut rd| rd.any(|e| e.ok().map(|e| e.path().extension() == Some("segment".as_ref())).unwrap_or(false)))
        .unwrap_or(false);

    if has_segments {
        recover(dir).with_context(|| format!("failed to recover log at {}", dir.display()))
    } else {
        LocalLog::create(dir, synapse_log::DEFAULT_MAX_RECORDS_PER_SEGMENT)
            .with_context(|| format!("failed to create log at {}", dir.display()))
    }
}

fn parse_value(raw: &str) -> Result<Value> {
    let trimmed = raw.trim();
    if trimmed == "null" {
        return Ok(Value::null());
    }
    if trimmed == "true" {
        return Ok(Value::bool(true));
    }
    if trimmed == "false" {
        return Ok(Value::bool(false));
    }
    // Integer.
    if let Ok(i) = trimmed.parse::<i64>() {
        return Ok(Value::i64(i));
    }
    // Float.
    if let Ok(f) = trimmed.parse::<f64>() {
        return Ok(Value::f64(f));
    }
    // Bytes written as a 0x-prefixed hex string.
    if let Some(hex_body) = trimmed.strip_prefix("0x").or_else(|| trimmed.strip_prefix("0X")) {
        let bytes = hex::decode(hex_body).context("invalid hex byte value")?;
        return Ok(Value::bytes(bytes));
    }
    // JSON string (surrounded by quotes).
    let value: serde_json::Value = serde_json::from_str(trimmed)
        .context("value must be valid JSON (null, true, number, string, or 0x... hex)")?;
    match value {
        serde_json::Value::String(s) => Ok(Value::string(s)),
        _ => bail!("unsupported JSON value; use --value with a primitive"),
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Init { dir, segments } => {
            let _log = LocalLog::create(&dir, segments)
                .with_context(|| format!("failed to create log at {}", dir.display()))?;
            println!("initialized SynapseDB at {}", dir.display());
            println!("max records per segment: {}", segments);
        }
        Command::Write {
            dir,
            entity,
            attr,
            value,
            ts,
            diff,
        } => {
            let log = open_log(&dir)?;
            let record = Record::new(
                EntityId::from_u128(entity),
                Attribute::new(attr),
                parse_value(&value)?,
                Timestamp::from_nanos(ts),
                diff.into(),
            );
            let pos = log
                .append(std::slice::from_ref(&record))
                .context("append failed")?;
            log.flush().context("flush failed")?;
            println!("written at offset {}", pos.as_offset());
        }
        Command::Read { dir, offset } => {
            let log = open_log(&dir)?;
            match log.read(LogPosition::from_offset(offset)) {
                Some(record) => println!("{}", record),
                None => println!("no record at offset {}", offset),
            }
        }
        Command::Snapshot { dir, as_of } => {
            let log = open_log(&dir)?;
            let records = log.snapshot_as_of(Timestamp::from_nanos(as_of));
            println!("snapshot as_of={} records={}", as_of, records.len());
            for record in records {
                println!("{}", record);
            }
        }
        Command::Verify { dir } => {
            let log = open_log(&dir)?;
            let root = log.latest_root();
            let count = log.total_records();
            println!("records: {}", count);
            match root {
                Some(h) => println!("mmr root: {}", hex::encode(h)),
                None => println!("mmr root: (empty log)"),
            }
        }
        Command::Recover { dir } => {
            let log = recover(&dir).with_context(|| format!("recovery failed at {}", dir.display()))?;
            println!(
                "recovered {} records from {}",
                log.total_records(),
                dir.display()
            );
            if let Some(root) = log.latest_root() {
                println!("mmr root: {}", hex::encode(root));
            }
        }
    }
    Ok(())
}

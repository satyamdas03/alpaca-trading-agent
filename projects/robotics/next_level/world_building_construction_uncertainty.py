import pybullet as p
import pybullet_data
import time
import http.client
import json
import re  
import math 
import numpy as np
import cv2
import os

# Local LLM config. Change this to any model available via `ollama list`.
OLLAMA_MODEL = "qwen3.5:latest"  # was llama3:8b; available in this environment

# --- PART 1: THE "PLANNER" (OLLAMA LLM COMMUNICATION) ---

def get_location_name(body_id):
    for name, info in WORLD_KNOWLEDGE.items():
        if info["type"] == "location":
            loc_id = info.get("id")
            if loc_id is not None:
                if get_distance(body_id, loc_id) < 0.5:
                    return name
    return "an unknown area"

def get_world_state_text(robot_name):
    print(f"Generating world state report for {robot_name}...")
    state_report = "\n--- CURRENT WORLD STATE ---\n"
    
    robot_id = ROBOT_STATE[robot_name]["id"]
    state_report += f"Robot is at: {get_location_name(robot_id)}\n"
    
    held_item = ROBOT_STATE[robot_name]["held_object_name"]
    if held_item:
        state_report += f"Robot is holding: {held_item}\n"
    else:
        state_report += "Robot is holding: nothing\n"
        
    state_report += "Object locations are UNKNOWN unless seen.\n"
    state_report += "-----------------------------\n"
    return state_report

def get_llm_plan(robot_name, user_command, failure_info=None, temperature=None):
    world_state = get_world_state_text(robot_name)
    
    system_prompt = """
    You are a robot controller. You convert a Command into a JSON list of objects.
    You MUST obey the Current World STATE and all Rules.

    FUNCTIONS (Use this format):
    - {"function": "move_to", "target": "target_name"}
    - {"function": "pickup", "target": "object_name"}
    - {"function": "place_at", "target": "x, y, z"}
    - {"function": "drop", "target": "location_name"}
    - {"function": "drop_here", "target": "none"}
    - {"function": "return_object", "target": "object_name"}

    TARGETS:
    - "block_red" (object)
    - "block_red_2" (object, also red)
    - "block_green" (object)
    - "block_blue" (object)
    - "start_area" (location)
    - "drop_zone" (location)

    RULES:
    1. Read the "CURRENT WORLD STATE".
    2. Object locations are UNKNOWN. To find an object, you MUST use `move_to("object_name")`.
    3. If the robot is holding an object, it MUST `place_at` or `drop` it before it can `pickup` another.
    4. "Place it at X, Y, Z" means: `place_at("X, Y, Z")`.
    5. If you just need to let go of an object, use `drop_here`.
    6. You MAY optionally include an "uncertainty" field per step (0.0 = certain, 1.0 = very uncertain). This is optional.
    7. You MUST respond with *only* the JSON list of objects. NO other text.
    """
    
    prompt_text = f"{system_prompt}\n{world_state}\n"
    
    if failure_info:
        print(f"\n!!! [{robot_name}] REPLANNING REQUIRED: {failure_info} !!!\n")
        prompt_text += f"PREVIOUS PLAN FAILED!\nFailure Reason: {failure_info}\n"
        prompt_text += f"The ORIGINAL COMMAND was: \"{user_command}\"\n"
        prompt_text += "Generate a NEW, FULL plan from scratch to achieve the original command.\nResponse:"
    else:
        print(f"[{robot_name}] Sending command to LLM: '{user_command}'...")
        prompt_text += f"Command: \"{user_command}\"\nResponse:"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_text,
        "stream": False
    }
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    
    max_retries = 3
    for i in range(max_retries):
        try:
            conn = http.client.HTTPConnection("localhost", 11434)
            conn.request("POST", "/api/generate", json.dumps(payload))
            response = conn.getresponse()
            
            if response.status != 200:
                print(f"[{robot_name}] Error from Ollama: {response.status} {response.reason}")
                return []
                
            response_body = response.read().decode('utf-8')
            conn.close()
            
            response_data = json.loads(response_body)
            llm_output_string = response_data.get('response', '[]')
            
            match = re.search(r'\[.*\]', llm_output_string, re.DOTALL)
            if not match:
                print(f"[{robot_name}] LLM Response did not contain a JSON list: {llm_output_string}")
                return []
            
            plan_json_string = match.group(0)
            plan = json.loads(plan_json_string)
            
            print(f"[{robot_name}] LLM generated plan: {plan}")
            return plan
            
        except ConnectionRefusedError:
            print(f"[{robot_name}] Connection refused. Retrying {i+1}/{max_retries}...")
            time.sleep(2)
        except Exception as e:
            print(f"[{robot_name}] Error communicating with Ollama: {e}")
            return []
            
    return []


def _step_key(step):
    """Canonical string representation of a plan step for ensemble comparison."""
    if not isinstance(step, dict):
        return json.dumps(step, sort_keys=True)
    return json.dumps({"function": step.get("function"), "target": step.get("target")}, sort_keys=True)


def _ensemble_uncertainty(plans):
    """
    Given a list of plans (each a list of dicts), return a single plan with
    per-step uncertainty scores derived from how often that step appears across
    the ensemble. Steps only present in some samples inherit the sample-max
    uncertainty of their position.
    """
    if not plans:
        return []
    n = len(plans)
    max_len = max(len(plan) for plan in plans)
    consensus = []
    for idx in range(max_len):
        votes = {}
        for plan in plans:
            if idx < len(plan):
                key = _step_key(plan[idx])
                votes[key] = votes.get(key, 0) + 1
        if not votes:
            continue
        # Pick the step with the most votes; tie-break by first occurrence order.
        best_key = max(votes, key=lambda k: (votes[k], -list(votes.keys()).index(k)))
        best_count = votes[best_key]
        uncertainty = 1.0 - (best_count / n)
        # Decode best_key back into a step dict.
        consensus_step = json.loads(best_key)
        consensus_step["uncertainty"] = round(uncertainty, 2)
        # Preserve any extra keys from the most-voted raw step (e.g., self-reported confidence).
        for plan in plans:
            if idx < len(plan) and _step_key(plan[idx]) == best_key:
                raw = plan[idx]
                if isinstance(raw, dict):
                    for k, v in raw.items():
                        if k not in consensus_step and k != "uncertainty":
                            consensus_step[k] = v
                break
        consensus.append(consensus_step)
    return consensus


def get_ensemble_plan(robot_name, user_command, failure_info=None, ensemble_size=3, temperature=0.8):
    """
    Generate multiple plans from the local LLM and fuse them into a single plan
    with ensemble-derived uncertainty scores.
    """
    print(f"[{robot_name}] Generating ensemble plan (n={ensemble_size}, T={temperature})...")
    plans = []
    for i in range(ensemble_size):
        plan = get_llm_plan(robot_name, user_command, failure_info=failure_info, temperature=temperature)
        if plan:
            plans.append(plan)
        else:
            print(f"[{robot_name}] Ensemble sample {i+1} failed.")
        time.sleep(0.1)
    if not plans:
        return []
    fused = _ensemble_uncertainty(plans)
    print(f"[{robot_name}] Fused ensemble plan: {fused}")
    return fused


# --- PART 2: THE "SIMULATOR & SKILLS" (PYBULLET ROBOTICS) ---

ROBOT_STATE = {
    "robot_0": {"id": None, "held_object_name": None, "current_constraint": None, "color": [1, 0, 0, 1]}, # Red
    "robot_1": {"id": None, "held_object_name": None, "current_constraint": None, "color": [0, 1, 0, 1]}, # Green
    "robot_2": {"id": None, "held_object_name": None, "current_constraint": None, "color": [0, 0, 1, 1]}  # Blue
}

WORLD_KNOWLEDGE = {
    "block_red":       {"pos": [2, 2, 0.05],     "id": None, "type": "object"},
    "block_red_2":     {"pos": [2, 2.5, 0.05],   "id": None, "type": "object"},
    "block_green":     {"pos": [2, -2, 0.05],    "id": None, "type": "object"},
    "block_blue":      {"pos": [0, 3, 0.05],     "id": None, "type": "object"},
    "drop_zone":       {"pos": [-2, 0, 0.01],    "id": None, "type": "location"},
    "start_area":      {"pos": [0, 0, 0.01],     "id": None, "type": "location"},
    "block_red_spawn": {"pos": [2, 2, 0.01],     "id": None, "type": "location"},
    "block_red_2_spawn":{"pos": [2, 2.5, 0.01],   "id": None, "type": "location"},
    "block_green_spawn":{"pos": [2, -2, 0.01],  "id": None, "type": "location"},
    "block_blue_spawn":{"pos": [0, 3, 0.01],     "id": None, "type": "location"}
}

CAM_IMG_WIDTH = 320
CAM_IMG_HEIGHT = 200

# Color Ranges
COLOR_RANGES = {
    "block_red": {
        'lower1': np.array([0, 100, 70]), 'upper1': np.array([10, 255, 255]),
        'lower2': np.array([170, 100, 70]), 'upper2': np.array([180, 255, 255])
    },
    "block_red_2": {
        'lower1': np.array([0, 100, 70]), 'upper1': np.array([10, 255, 255]),
        'lower2': np.array([170, 100, 70]), 'upper2': np.array([180, 255, 255])
    },
    "block_green": {
        'lower1': np.array([40, 100, 70]), 'upper1': np.array([80, 255, 255]),
        'lower2': None, 'upper2': None
    },
    "block_blue": {
        'lower1': np.array([100, 100, 70]), 'upper1': np.array([140, 255, 255]),
        'lower2': None, 'upper2': None
    }
}


def setup_simulation():
    print("Setting up Construction Site...")
    if os.environ.get("BULL_DIRECT") == "1":
        physicsClient = p.connect(p.DIRECT)
        print("BULL_DIRECT=1: connected to DIRECT mode.")
    else:
        try:
            physicsClient = p.connect(p.GUI)
            print("Connected to new PyBullet GUI.")
        except p.error:
            physicsClient = p.connect(p.DIRECT)
            print("Could not connect to GUI, connected to DIRECT.")

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # Reset Python-side mental state on every setup.
    for name in ROBOT_STATE:
        ROBOT_STATE[name]["held_object_name"] = None
        ROBOT_STATE[name]["current_constraint"] = None

    start_positions = [[-1, 0, 0.05], [0, 0, 0.05], [1, 0, 0.05]]

    for i, robot_name in enumerate(ROBOT_STATE.keys()):
        start_pos = start_positions[i]
        robot_id = p.loadURDF("r2d2.urdf", start_pos)
        ROBOT_STATE[robot_name]["id"] = robot_id
        p.changeVisualShape(robot_id, -1, rgbaColor=ROBOT_STATE[robot_name]["color"])

    # Setup Blocks (Boxes)
    block_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.1, 0.1, 0.1])
    
    block_red_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.1, 0.1, 0.1], rgbaColor=[1, 0, 0, 1])
    WORLD_KNOWLEDGE["block_red"]["id"] = p.createMultiBody(
        baseMass=0.1, baseCollisionShapeIndex=block_shape,
        baseVisualShapeIndex=block_red_visual, basePosition=WORLD_KNOWLEDGE["block_red"]["pos"]
    )
    # FIX: Physics properties
    p.changeDynamics(WORLD_KNOWLEDGE["block_red"]["id"], -1, lateralFriction=1.0, restitution=0.1, linearDamping=0.5, angularDamping=0.5)

    WORLD_KNOWLEDGE["block_red_2"]["id"] = p.createMultiBody(
        baseMass=0.1, baseCollisionShapeIndex=block_shape,
        baseVisualShapeIndex=block_red_visual, basePosition=WORLD_KNOWLEDGE["block_red_2"]["pos"]
    )
    p.changeDynamics(WORLD_KNOWLEDGE["block_red_2"]["id"], -1, lateralFriction=1.0, restitution=0.1, linearDamping=0.5, angularDamping=0.5)

    block_green_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.1, 0.1, 0.1], rgbaColor=[0, 1, 0, 1])
    WORLD_KNOWLEDGE["block_green"]["id"] = p.createMultiBody(
        baseMass=0.1, baseCollisionShapeIndex=block_shape,
        baseVisualShapeIndex=block_green_visual, basePosition=WORLD_KNOWLEDGE["block_green"]["pos"]
    )
    # FIX: Physics properties
    p.changeDynamics(WORLD_KNOWLEDGE["block_green"]["id"], -1, lateralFriction=1.0, restitution=0.1, linearDamping=0.5, angularDamping=0.5)
    
    block_blue_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.1, 0.1, 0.1], rgbaColor=[0, 0, 1, 1])
    WORLD_KNOWLEDGE["block_blue"]["id"] = p.createMultiBody(
        baseMass=0.1, baseCollisionShapeIndex=block_shape,
        baseVisualShapeIndex=block_blue_visual, basePosition=WORLD_KNOWLEDGE["block_blue"]["pos"]
    )
    # FIX: Physics properties
    p.changeDynamics(WORLD_KNOWLEDGE["block_blue"]["id"], -1, lateralFriction=1.0, restitution=0.1, linearDamping=0.5, angularDamping=0.5)

    # Setup Locations
    zone_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 0.01])
    zone_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 0.01], rgbaColor=[0, 1, 0, 0.5])
    WORLD_KNOWLEDGE["drop_zone"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=zone_shape,
        baseVisualShapeIndex=zone_visual, basePosition=WORLD_KNOWLEDGE["drop_zone"]["pos"]
    )
    
    start_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 0.01])
    start_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 0.01], rgbaColor=[0.5, 0.5, 0.5, 0.5])
    WORLD_KNOWLEDGE["start_area"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=start_shape,
        baseVisualShapeIndex=start_visual, basePosition=WORLD_KNOWLEDGE["start_area"]["pos"]
    )
    
    # Spawn markers
    spawn_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.005])
    spawn_visual_red = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.005], rgbaColor=[1, 0, 0, 0.3])
    spawn_visual_green = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.005], rgbaColor=[0, 1, 0, 0.3])
    spawn_visual_blue = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.005], rgbaColor=[0, 0, 1, 0.3])

    WORLD_KNOWLEDGE["block_red_spawn"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=spawn_shape,
        baseVisualShapeIndex=spawn_visual_red, basePosition=WORLD_KNOWLEDGE["block_red_spawn"]["pos"]
    )
    WORLD_KNOWLEDGE["block_red_2_spawn"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=spawn_shape,
        baseVisualShapeIndex=spawn_visual_red, basePosition=WORLD_KNOWLEDGE["block_red_2_spawn"]["pos"]
    )
    WORLD_KNOWLEDGE["block_green_spawn"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=spawn_shape,
        baseVisualShapeIndex=spawn_visual_green, basePosition=WORLD_KNOWLEDGE["block_green_spawn"]["pos"]
    )
    WORLD_KNOWLEDGE["block_blue_spawn"]["id"] = p.createMultiBody(
        baseMass=0, baseCollisionShapeIndex=spawn_shape,
        baseVisualShapeIndex=spawn_visual_blue, basePosition=WORLD_KNOWLEDGE["block_blue_spawn"]["pos"]
    )
    
    print("Construction Site Ready.")

# --- ROBOT "SKILLS" ---

def get_current_pos(body_id):
    pos, _ = p.getBasePositionAndOrientation(body_id)
    return pos[0], pos[1]

def get_distance(objA_id, objB_id):
    posA = get_current_pos(objA_id)
    posB = get_current_pos(objB_id)
    return math.sqrt((posA[0] - posB[0])**2 + (posA[1] - posB[1])**2)


# --- WORLD SNAPSHOT / ROLLBACK (for uncertainty-driven physics rollouts) ---

def _body_snapshot(body_id):
    pos, orn = p.getBasePositionAndOrientation(body_id)
    vel = p.getBaseVelocity(body_id)
    return {
        "id": body_id,
        "pos": pos,
        "orn": orn,
        "lin_vel": vel[0],
        "ang_vel": vel[1]
    }


def save_world_state():
    """
    Capture a full, deterministic snapshot of the simulation plus the Python-side
    robot mental state. Must be paired with load_world_state().
    """
    state = {
        "pybullet_state_id": p.saveState(),
        "robot_state": {
            name: {
                "held_object_name": data["held_object_name"],
                "current_constraint": data["current_constraint"]
            }
            for name, data in ROBOT_STATE.items()
        },
        "body_snapshots": [_body_snapshot(data["id"]) for data in WORLD_KNOWLEDGE.values() if data.get("id") is not None],
        "time": time.time()
    }
    return state


def load_world_state(state):
    """
    Restore a snapshot captured by save_world_state().
    PyBullet restoreState handles most physics; we explicitly reset base velocities
    and the Python-side robot mental state to be safe.
    """
    if state is None:
        return
    p.restoreState(stateId=state["pybullet_state_id"])
    # Explicitly restore velocities because restoreState can leave stale impulses.
    for snap in state.get("body_snapshots", []):
        p.resetBaseVelocity(snap["id"], snap["lin_vel"], snap["ang_vel"])
    # Restore Python mental state.
    for name, data in state["robot_state"].items():
        ROBOT_STATE[name]["held_object_name"] = data["held_object_name"]
        ROBOT_STATE[name]["current_constraint"] = data["current_constraint"]


def _step_has_contact_forces(max_force=50.0):
    """Return True if any contact force exceeds the threshold."""
    contacts = p.getContactPoints()
    for c in contacts:
        # normal force is at index 9 in PyBullet contact tuple
        if len(c) > 9 and c[9] > max_force:
            return True
    return False


def simulate_branch(robot_name, plan_steps, horizon_seconds=0.5, sleep_per_step=0.0):
    """
    Execute a sequence of plan steps in a fast, reversible physics rollout.
    Returns (success, failed_step_info, metrics).

    This function MUST be called from the same PyBullet client; it uses
    save/load world state to roll back after the rollout.
    """
    if not plan_steps:
        return True, None, {"rollout_steps": 0, "contacts_exceeded": False}

    print(f"[{robot_name}] UNCERTAINTY: running physics rollout for {len(plan_steps)} step(s)...")
    snapshot = save_world_state()
    metrics = {
        "rollout_steps": len(plan_steps),
        "contacts_exceeded": False,
        "final_positions": {}
    }

    # Run rollouts at maximum speed (sleep_per_step=0 by default).
    for step in plan_steps:
        function_name = step.get("function")
        parameter = step.get("target")
        if function_name == "drop_here":
            parameter = "none"
        success = False
        try:
            if function_name == "move_to":
                success = move_to(robot_name, parameter)
            elif function_name == "pickup":
                success = pickup(robot_name, parameter)
            elif function_name == "drop":
                success = drop(robot_name, parameter)
            elif function_name == "drop_here":
                success = drop(robot_name, None)
            elif function_name == "place_at":
                success = place_at(robot_name, parameter)
            elif function_name == "return_object":
                success = return_object(robot_name, parameter)
            else:
                print(f"[{robot_name}] Unknown command in rollout: {function_name}")
                success = True
        except Exception as e:
            print(f"[{robot_name}] Rollout step exception: {e}")
            success = False

        if _step_has_contact_forces():
            metrics["contacts_exceeded"] = True

        if not success:
            metrics["failed_step"] = step
            load_world_state(snapshot)
            print(f"[{robot_name}] Rollout FAILED at step {step}; world restored.")
            return False, step, metrics

    # Capture final positions of all objects for later analysis.
    for name, info in WORLD_KNOWLEDGE.items():
        if info.get("id") is not None and info["type"] == "object":
            pos, _ = p.getBasePositionAndOrientation(info["id"])
            metrics["final_positions"][name] = pos

    load_world_state(snapshot)
    print(f"[{robot_name}] Rollout SUCCEEDED; world restored.")
    return True, None, metrics


# --- ROBOT "SKILLS" ---

def get_camera_image_and_find(robot_name, target_name):
    if target_name not in COLOR_RANGES:
        print(f"[{robot_name}] Error: No color definition for {target_name}")
        return False, None

    robot_id = ROBOT_STATE[robot_name]["id"] 
    pos, orn = p.getBasePositionAndOrientation(robot_id)
    
    rot_matrix = p.getMatrixFromQuaternion(orn)
    rot_matrix = np.array(rot_matrix).reshape(3, 3)
    
    camera_offset = [0.2, 0, 0.3] 
    target_offset = [1.5, 0, 0.0] 
    
    camera_pos = pos + rot_matrix.dot(camera_offset) 
    target_pos = pos + rot_matrix.dot(target_offset)

    view_matrix = p.computeViewMatrix(camera_pos, target_pos, [0, 0, 1])
    projection_matrix = p.computeProjectionMatrixFOV(
        fov=90.0,
        aspect=float(CAM_IMG_WIDTH) / CAM_IMG_HEIGHT,
        nearVal=0.1,
        farVal=100.0
    )
    
    (_, _, rgbImg, _, _) = p.getCameraImage(
        width=CAM_IMG_WIDTH,
        height=CAM_IMG_HEIGHT,
        viewMatrix=view_matrix,
        projectionMatrix=projection_matrix,
        renderer=p.ER_BULLET_HARDWARE_OPENGL 
    )
    
    rgbImg = np.array(rgbImg, dtype=np.uint8)
    
    if len(rgbImg.shape) == 1:
        rgbImg = rgbImg.reshape((CAM_IMG_HEIGHT, CAM_IMG_WIDTH, 4))
        
    try:
        img_bgr = cv2.cvtColor(rgbImg, cv2.COLOR_RGBA2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        colors = COLOR_RANGES[target_name]
        
        mask1 = cv2.inRange(img_hsv, colors['lower1'], colors['upper1'])
        
        if colors['lower2'] is not None:
            mask2 = cv2.inRange(img_hsv, colors['lower2'], colors['upper2'])
            mask = mask1 | mask2
        else:
            mask = mask1
            
        if np.sum(mask) > 50: 
            return True, mask 
        else:
            return False, None
    except Exception as e:
        print(f"[{robot_name}] Error processing camera image: {e}")
        return False, None

def find_object(robot_name, target_name):
    print(f"[{robot_name}] SKILL: Finding '{target_name}'...")
    
    if ROBOT_STATE[robot_name]["held_object_name"] == target_name:
        print(f"[{robot_name}] Already holding {target_name}.")
        return True
    
    target_id = WORLD_KNOWLEDGE[target_name]["id"]
    robot_id = ROBOT_STATE[robot_name]["id"]
    
    distance = get_distance(robot_id, target_id)
    if distance < 0.5:
        print(f"[{robot_name}] Object {target_name} is already at my feet.")
        return True
    
    for i in range(20):
        found, _ = get_camera_image_and_find(robot_name, target_name) 
        if found:
            print(f"[{robot_name}] Found {target_name}!")
            return True
            
        current_pos, current_orn = p.getBasePositionAndOrientation(robot_id)
        yaw = p.getEulerFromQuaternion(current_orn)[2]
        next_yaw = yaw + (math.pi * 2 / 20)
        next_orn = p.getQuaternionFromEuler([0, 0, next_yaw])
        
        p.resetBasePositionAndOrientation(robot_id, current_pos, next_orn)
        
        for _ in range(10):
            p.stepSimulation()
            time.sleep(0.01)
            
    print(f"[{robot_name}] Could not find {target_name} after spinning 360 degrees.")
    return False

def _navigate_to_coords(robot_name, target_pos, threshold=0.4):
    robot_id = ROBOT_STATE[robot_name]["id"]
    
    for _ in range(2000):
        current_pos, _ = p.getBasePositionAndOrientation(robot_id)
        
        dir_x = target_pos[0] - current_pos[0]
        dir_y = target_pos[1] - current_pos[1]
        distance = math.sqrt(dir_x**2 + dir_y**2)
        
        if distance < threshold:
            p.resetBaseVelocity(robot_id, [0, 0, 0]) 
            return True 
        
        speed = min(2.0, max(0.2, distance * 2.0))
        
        norm_x = dir_x / distance
        norm_y = dir_y / distance
        linear_velocity = [norm_x * speed, norm_y * speed, 0]
        target_yaw = math.atan2(dir_y, dir_x)
        target_orn = p.getQuaternionFromEuler([0, 0, target_yaw])
        
        p.resetBasePositionAndOrientation(robot_id, current_pos, target_orn)
        p.resetBaseVelocity(robot_id, linear_velocity, [0, 0, 0])
        
        p.stepSimulation()
        time.sleep(0.01)
        
    p.resetBaseVelocity(robot_id, [0, 0, 0]) 
    print(f"[{robot_name}] Navigation timed out.")
    return False

def move_to(robot_name, target_name):
    print(f"[{robot_name}] SKILL: Navigating to '{target_name}'...")
    if target_name not in WORLD_KNOWLEDGE:
        print(f"[{robot_name}] Error: Unknown target '{target_name}'")
        return False
    
    target_info = WORLD_KNOWLEDGE[target_name]
    
    if target_info["type"] == "location":
        print(f"[{robot_name}] {target_name} is a location. Moving to known coordinates.")
        if _navigate_to_coords(robot_name, target_info["pos"]):
            print(f"[{robot_name}] Arrived at {target_name}.")
            return True
        return False
            
    elif target_info["type"] == "object":
        print(f"[{robot_name}] {target_name} is an object. Trying to find it...")
        if find_object(robot_name, target_name):
            if ROBOT_STATE[robot_name]["held_object_name"] == target_name:
                print(f"[{robot_name}] Already holding {target_name}, no need to move.")
                return True
                
            target_id = target_info["id"]
            target_pos_tuple, _ = p.getBasePositionAndOrientation(target_id)
            print(f"[{robot_name}] Object {target_name} located. Moving to its position.")
            if _navigate_to_coords(robot_name, target_pos_tuple):
                print(f"[{robot_name}] Arrived at {target_name}.")
                return True
        else:
            print(f"[{robot_name}] Failed to move to {target_name} (could not find it).")
            return False
    return False

def pickup(robot_name, object_name):
    print(f"[{robot_name}] SKILL: Attempting to pick up '{object_name}'...")
    if object_name not in WORLD_KNOWLEDGE:
        print(f"[{robot_name}] Error: Unknown object '{object_name}'")
        return False
    if WORLD_KNOWLEDGE[object_name]["type"] != "object":
        print(f"[{robot_name}] Error: Cannot 'pickup' a location: {object_name}")
        return False
        
    if ROBOT_STATE[robot_name]["current_constraint"] is not None:
        print(f"[{robot_name}] Robot is already holding an object ({ROBOT_STATE[robot_name]['held_object_name']}).")
        return False

    robot_id = ROBOT_STATE[robot_name]["id"]
    object_id = WORLD_KNOWLEDGE[object_name]["id"]
    
    pickup_distance = 0.45 
    
    distance = get_distance(robot_id, object_id)
    if distance > pickup_distance:
        print(f"[{robot_name}] Error: '{object_name}' is too far away ({distance:.2f} units). Moving to it first...")
        if not move_to(robot_name, object_name):
            return False
    
    distance = get_distance(robot_id, object_id)
    if distance > pickup_distance:
        print(f"[{robot_name}] Failed to get close enough to {object_name} (distance: {distance:.2f}). Pickup failed.")
        return False

    constraint_id = p.createConstraint(
        parentBodyUniqueId=robot_id,
        parentLinkIndex=-1, 
        childBodyUniqueId=object_id,
        childLinkIndex=-1,
        jointType=p.JOINT_FIXED,
        jointAxis=[0, 0, 0],
        parentFramePosition=[0.5, 0, 0.6],
        childFramePosition=[0, 0, 0]
    )
    ROBOT_STATE[robot_name]["current_constraint"] = constraint_id
    ROBOT_STATE[robot_name]["held_object_name"] = object_name 
    print(f"[{robot_name}] Picked up {object_name} (holding in front).")
    
    for _ in range(50):
        p.stepSimulation()
        time.sleep(0.01)
    return True

def drop(robot_name, location_name):
    if location_name is None or str(location_name).lower() == "none":
        print(f"[{robot_name}] Dropping object right here.")
        if ROBOT_STATE[robot_name]["current_constraint"] is None:
            print(f"[{robot_name}] Robot is not holding anything.")
            return True # Technically success
            
        p.removeConstraint(ROBOT_STATE[robot_name]["current_constraint"])
        ROBOT_STATE[robot_name]["current_constraint"] = None
        ROBOT_STATE[robot_name]["held_object_name"] = None 
        return True

    print(f"[{robot_name}] SKILL: Attempting to drop at '{location_name}'...")
    if location_name not in WORLD_KNOWLEDGE:
        print(f"[{robot_name}] Error: Unknown location '{location_name}'")
        return False
        
    target_info = WORLD_KNOWLEDGE[location_name]
    if target_info["type"] != "location":
        print(f"[{robot_name}] Error: Cannot 'drop' at an object. '{location_name}' is not a location.")
        return False
        
    if ROBOT_STATE[robot_name]["current_constraint"] is None:
        print(f"[{robot_name}] Robot is not holding anything.")
        return False
    
    robot_id = ROBOT_STATE[robot_name]["id"]
    drop_zone_id = target_info["id"] 

    drop_distance = 0.45 

    distance = get_distance(robot_id, drop_zone_id)
    if distance > drop_distance:
        print(f"[{robot_name}] Error: Not at '{location_name}' ({distance:.2f} units). Moving to it first...")
        if not move_to(robot_name, location_name):
            return False
    
    distance = get_distance(robot_id, drop_zone_id)
    if distance > drop_distance:
        print(f"[{robot_name}] Failed to get close enough to {location_name}. Drop failed.")
        return False

    p.removeConstraint(ROBOT_STATE[robot_name]["current_constraint"])
    ROBOT_STATE[robot_name]["current_constraint"] = None
    ROBOT_STATE[robot_name]["held_object_name"] = None 
    print(f"[{robot_name}] Dropped object.")
    
    for _ in range(50):
        p.stepSimulation()
        time.sleep(0.01)
    return True

def place_at(robot_name, target_coords_str):
    print(f"[{robot_name}] SKILL: Attempting to place at '{target_coords_str}'...")
    
    try:
        coords = [float(x.strip()) for x in target_coords_str.split(',')]
        if len(coords) != 3:
            print(f"[{robot_name}] Error: Invalid coordinates '{target_coords_str}'")
            return False
    except ValueError:
        print(f"[{robot_name}] Error: Could not parse coordinates '{target_coords_str}'")
        return False

    if ROBOT_STATE[robot_name]["current_constraint"] is None:
        print(f"[{robot_name}] Error: Cannot place. Robot is not holding anything.")
        return False
        
    held_obj_name = ROBOT_STATE[robot_name]["held_object_name"]
    if not held_obj_name:
        print(f"[{robot_name}] Error: State says holding nothing (name is None).")
        return False
        
    object_id = WORLD_KNOWLEDGE[held_obj_name]["id"]
    robot_id = ROBOT_STATE[robot_name]["id"]

    # --- OFFSET PLACEMENT LOGIC ---
    # 1. Calculate Standoff Position (0.5m away from target)
    current_pos, _ = p.getBasePositionAndOrientation(robot_id)
    dx = coords[0] - current_pos[0]
    dy = coords[1] - current_pos[1]
    angle_to_target = math.atan2(dy, dx)
    
    # Target position for the ROBOT BODY (0.5m away from block target)
    standoff_dist = 0.5
    stand_x = coords[0] - math.cos(angle_to_target) * standoff_dist
    stand_y = coords[1] - math.sin(angle_to_target) * standoff_dist
    stand_pos = [stand_x, stand_y, 0]

    print(f"[{robot_name}] Moving to Standoff Position {stand_pos} (Offset Placement)...")
    
    if _navigate_to_coords(robot_name, stand_pos, threshold=0.05):
        print(f"[{robot_name}] Arrived at Standoff. Aligning to face target...")
        
        # 2. Force Orientation to face target exactly
        target_orn = p.getQuaternionFromEuler([0, 0, angle_to_target])
        p.resetBasePositionAndOrientation(robot_id, [stand_x, stand_y, 0], target_orn)
        
        # Stop any residual motion
        p.resetBaseVelocity(robot_id, [0, 0, 0], [0, 0, 0])
        for _ in range(20): p.stepSimulation(); time.sleep(0.01)

        print(f"[{robot_name}] Aligned. Freezing robot for stable placement...")
        
        # FIX: Freeze robot to prevent tipping
        original_dynamics = p.getDynamicsInfo(robot_id, -1)
        original_mass = original_dynamics[0]
        p.changeDynamics(robot_id, -1, mass=0)  # Make immovable
        p.resetBaseVelocity(robot_id, [0, 0, 0], [0, 0, 0])
        
        print(f"[{robot_name}] Robot stabilized. Lowering object gently...")
        
        constraint_id = ROBOT_STATE[robot_name]["current_constraint"]
        
        start_height = 0.6
        target_relative_height = coords[2] + 0.02
        
        steps = 100 
        for i in range(steps):
            h = start_height - (start_height - target_relative_height) * (i / steps)
            
            p.removeConstraint(constraint_id)
            constraint_id = p.createConstraint(
                parentBodyUniqueId=robot_id,
                parentLinkIndex=-1, 
                childBodyUniqueId=object_id,
                childLinkIndex=-1,
                jointType=p.JOINT_FIXED,
                jointAxis=[0, 0, 0],
                parentFramePosition=[0.5, 0, h],
                childFramePosition=[0, 0, 0]
            )
            ROBOT_STATE[robot_name]["current_constraint"] = constraint_id
            
            # FIX: Keep robot locked during lowering
            p.resetBaseVelocity(robot_id, [0, 0, 0], [0, 0, 0])
            
            p.stepSimulation()
            time.sleep(0.01)
        
        # FIX: Teleport block to exact target position
        print(f"[{robot_name}] Correcting block position to exact target...")
        level_orn = p.getQuaternionFromEuler([0, 0, 0])
        p.resetBasePositionAndOrientation(object_id, coords, level_orn)
        
        # FIX: Increased stabilization with both robot and block frozen
        for _ in range(50):  # Increased from 30
            p.resetBaseVelocity(robot_id, [0, 0, 0], [0, 0, 0])
            p.resetBaseVelocity(object_id, [0, 0, 0], [0, 0, 0])  # Also freeze block
            p.stepSimulation()
            time.sleep(0.01)

        # Release constraint
        p.removeConstraint(constraint_id)
        ROBOT_STATE[robot_name]["current_constraint"] = None
        ROBOT_STATE[robot_name]["held_object_name"] = None 
        print(f"[{robot_name}] Placed object at {coords}.")
        
        # FIX: Increase block friction to prevent sliding/falling
        p.changeDynamics(object_id, -1, 
            lateralFriction=2.0,      # Increased from default
            spinningFriction=0.5,
            rollingFriction=0.5)
        
        # FIX: Keep robot frozen even after release for settling
        print(f"[{robot_name}] Waiting for block to settle...")
        for _ in range(50):  # NEW: Additional settling time
            p.resetBaseVelocity(robot_id, [0, 0, 0], [0, 0, 0])
            p.stepSimulation()
            time.sleep(0.01)
        
        # FIX: NOW restore robot mobility for retreat
        p.changeDynamics(robot_id, -1, mass=original_mass)
        
        # FIX: Improved retreat - move perpendicular first to clear stack area
        print(f"[{robot_name}] Moving sideways to clear stack...")
        perp_angle = angle_to_target + math.pi/2  # 90 degrees perpendicular
        for _ in range(30):
            sx = math.cos(perp_angle) * 0.15
            sy = math.sin(perp_angle) * 0.15
            p.resetBaseVelocity(robot_id, [sx, sy, 0], [0, 0, 0])
            p.stepSimulation()
            time.sleep(0.01)
        
        # BACKUP MANEUVER
        print(f"[{robot_name}] Backing up...")
        for _ in range(40):
            bx = -math.cos(angle_to_target) * 0.2
            by = -math.sin(angle_to_target) * 0.2
            p.resetBaseVelocity(robot_id, [bx, by, 0], [0, 0, 0])
            p.stepSimulation()
            time.sleep(0.01)
        
        # Retreat to safe zone
        print(f"[{robot_name}] Retreating to safe zone...")
        retreat_map = {
            "robot_0": [-2, -2, 0],
            "robot_1": [-2, 0, 0],
            "robot_2": [-2, 2, 0]
        }
        safe_pos = retreat_map.get(robot_name, [-3, 0, 0])
        _navigate_to_coords(robot_name, safe_pos, threshold=0.5)
        
        return True
    else:
        print(f"[{robot_name}] Failed to reach standoff coordinates.")
        return False

def return_object(robot_name, object_name):
    print(f"[{robot_name}] SKILL: Attempting to return '{object_name}'...")
    if object_name not in WORLD_KNOWLEDGE or WORLD_KNOWLEDGE[object_name]["type"] != "object":
        print(f"[{robot_name}] Error: Unknown object {object_name}")
        return False

    if ROBOT_STATE[robot_name]["held_object_name"] != object_name:
        print(f"[{robot_name}] Error: Not holding {object_name}. Attempting to pick it up first.")
        if not pickup(robot_name, object_name):
            print(f"[{robot_name}] Failed to pick up {object_name}.")
            return False
            
    spawn_name = f"{object_name}_spawn"
    if spawn_name not in WORLD_KNOWLEDGE:
        print(f"[{robot_name}] Error: No spawn location defined for {object_name}.")
        return False
        
    print(f"[{robot_name}] Moving to {spawn_name} to drop {object_name}.")
    if move_to(robot_name, spawn_name):
        return drop(robot_name, spawn_name)
    
    return False

# --- PART 3: THE "EXECUTOR" (MAIN SCRIPT LOGIC) ---

UNCERTAINTY_ROLLOUT_THRESHOLD = 0.6  # Steps with uncertainty >= this get a physics rollout first.

# Shared runtime metrics, updated by parse_and_execute and printed by main().
RUNTIME_METRICS = {
    "ensemble_plans_generated": 0,
    "single_plans_generated": 0,
    "rollouts_run": 0,
    "rollout_rejections": 0,
    "replan_attempts": 0,
    "steps_executed": 0,
    "failed_steps": 0
}


def parse_and_execute(robot_name, plan):
    global RUNTIME_METRICS
    if not plan:
        print(f"[{robot_name}] Plan is empty. Nothing to do.")
        return True, None

    print(f"--- [{robot_name}] EXECUTING PLAN ---")

    for i, step in enumerate(plan):
        try:
            if not isinstance(step, dict):
                print(f"[{robot_name}] Error: Plan step is not a valid object: {step}")
                continue

            function_name = step.get("function")
            parameter = step.get("target")
            uncertainty = step.get("uncertainty", 0.0)

            if not function_name or not parameter:
                 # Allow drop_here with no target
                if function_name == "drop_here":
                    parameter = "none"
                else:
                    print(f"[{robot_name}] Error: Plan step is malformed: {step}")
                    continue

            RUNTIME_METRICS["steps_executed"] += 1

            # --- Uncertainty-driven physics rollout ---
            if uncertainty >= UNCERTAINTY_ROLLOUT_THRESHOLD:
                RUNTIME_METRICS["rollouts_run"] += 1
                # Roll out this step plus the remaining plan to catch future collisions.
                lookahead = plan[i:]
                rollout_ok, failed_step, metrics = simulate_branch(
                    robot_name,
                    lookahead,
                    horizon_seconds=0.5,
                    sleep_per_step=0.0
                )
                if not rollout_ok:
                    RUNTIME_METRICS["rollout_rejections"] += 1
                    print(f"!!! [{robot_name}] ROLLOUT REJECTED STEP: {function_name}({parameter}) due to physics collision/failure !!!")
                    return False, step
                if metrics.get("contacts_exceeded"):
                    RUNTIME_METRICS["rollout_rejections"] += 1
                    print(f"!!! [{robot_name}] ROLLOUT REJECTED STEP: {function_name}({parameter}) due to excessive contact forces !!!")
                    return False, step

            success = False
            if function_name == "move_to":
                success = move_to(robot_name, parameter)
            elif function_name == "pickup":
                success = pickup(robot_name, parameter)
            elif function_name == "drop":
                success = drop(robot_name, parameter)
            elif function_name == "drop_here":
                success = drop(robot_name, None)
            elif function_name == "place_at":
                success = place_at(robot_name, parameter)
            elif function_name == "return_object":
                success = return_object(robot_name, parameter)
            else:
                print(f"[{robot_name}] Unknown command in plan: {function_name}")
                success = True

            if not success:
                print(f"!!! [{robot_name}] STEP FAILED: {function_name}({parameter}) !!!")
                return False, step

        except Exception as e:
            print(f"[{robot_name}] Error executing step '{step}': {e}")
            return False, step

    print(f"--- [{robot_name}] PLAN COMPLETE ---")
    return True, None


def main():
    setup_simulation()
    
    print("\n" + "="*30)
    print("  CONSTRUCTION SITE READY. MODE: MULTI-ROBOT STACKING.")
    print("="*30)
    print(f"  Using model: {OLLAMA_MODEL}")
    print("  Mode: Sequential Foreman")
    print("  VISION: OpenCV Enabled")
    print("="*30)

    # Toggle between single LLM plan and ensemble uncertainty fusion.
    USE_ENSEMBLE = True

    # Initial commands for each robot (Red-Blue alternating wall demo)
    # Goal: build a horizontal wall of three alternating-colored blocks.
    commands = {
        "robot_0": "Get block_red and place it at -2.25, 0, 0.1",
        "robot_1": "Get block_blue and place it at -2.0, 0, 0.1",
        "robot_2": "Get block_red_2 and place it at -1.75, 0, 0.1"
    }

    # Keep track of failures to enable replanning
    failures = {
        "robot_0": None,
        "robot_1": None,
        "robot_2": None
    }

    print(f"Ensure Ollama is running with a model named '{OLLAMA_MODEL}' before starting.")
    print("Set USE_ENSEMBLE=False in main() to use a single deterministic plan.")
    if os.environ.get("BULL_AUTO_START") == "1":
        print("BULL_AUTO_START=1 detected. Skipping manual input prompt.")
    else:
        input("Press Enter to start the simulation loop...")

    all_done = False
    post_done_counter = 0

    while True:
        if all_done:
            post_done_counter += 1
            if post_done_counter > 200:  # ~2 seconds of settling, then exit
                print("\n[Bull] Demo complete. Exiting simulation.")
                break

        for robot_name in commands.keys():
            # Skip if command is None (finished)
            if commands[robot_name] is None:
                continue

            print(f"\n--- FOREMAN: {robot_name}, {commands[robot_name]} ---")

            # 1. Get Plan (with failure info if needed)
            if USE_ENSEMBLE:
                plan = get_ensemble_plan(robot_name, commands[robot_name], failures[robot_name])
                RUNTIME_METRICS["ensemble_plans_generated"] += 1
            else:
                plan = get_llm_plan(robot_name, commands[robot_name], failures[robot_name])
                RUNTIME_METRICS["single_plans_generated"] += 1

            if failures[robot_name] is not None:
                RUNTIME_METRICS["replan_attempts"] += 1

            # 2. Execute Plan
            success, error_message = parse_and_execute(robot_name, plan)

            if success:
                print(f"[{robot_name}] Task complete! Waiting for new command...")
                # Mark as done for this demo
                commands[robot_name] = None
                failures[robot_name] = None
            else:
                print(f"[{robot_name}] Task failed. Will replan next cycle.")
                failures[robot_name] = error_message
                RUNTIME_METRICS["failed_steps"] += 1

        if not all_done and all(c is None for c in commands.values()):
            all_done = True
            print("\n" + "="*40)
            print("  DEMO COMPLETE — FINAL METRICS")
            print("="*40)
            for key, value in RUNTIME_METRICS.items():
                print(f"  {key}: {value}")
            print("="*40)

        p.stepSimulation()
        time.sleep(0.01)

if __name__ == "__main__":
    main()

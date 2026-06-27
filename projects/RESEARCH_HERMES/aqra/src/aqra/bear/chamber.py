import json
import re

from aqra.bear.prompts import BEAR_PROMPT
from aqra.bear.review import BEARReview


class BEARChamber:
    def __init__(self, use_llm: bool = False, anthropic_client=None):
        self.use_llm = use_llm
        self.client = anthropic_client

    def review(self, dossier) -> BEARReview:
        if not self.use_llm or self.client is None:
            return self._mock_review(dossier)
        prompt = BEAR_PROMPT.format(
            id=dossier.candidate.id,
            lane=dossier.candidate.lane.value,
            formula=dossier.candidate.formula,
            rationale=dossier.candidate.rationale,
            metrics=json.dumps(dossier.metrics),
        )
        # Anthropic call placeholder
        response = self.client.messages.create(model="claude-3-haiku-20240307", max_tokens=512, messages=[{"role": "user", "content": prompt}])
        text = response.content[0].text
        return self._parse(text)

    def _mock_review(self, dossier) -> BEARReview:
        # Conservative mock: reject if turnover too high or no rationale
        passed = bool(dossier.candidate.rationale) and dossier.metrics.get("turnover", 0) < 5.0
        return BEARReview(
            passed=passed,
            look_ahead_bias=False,
            data_mining=False,
            lane_misclassification=False,
            economic_rationale=bool(dossier.candidate.rationale),
            robustness=True,
            summary="Mock review: pass" if passed else "Mock review: fail",
        )

    def _parse(self, text: str) -> BEARReview:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(match.group(0)) if match else {}
        return BEARReview(**data)

"""Census of the saved request bodies (quality_check/*_request.txt) for sampling and token settings."""
import collections
import glob
import json
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"


def main():
    keys, tc = collections.Counter(), collections.Counter()
    n = cap = samp = 0
    for f in sorted(glob.glob(str(corpus.SAVED / "railway-research-*" / "game-*" / "quality_check" / "*_request.txt"))):
        d = json.loads(Path(f).read_text())
        n += 1
        keys.update(k for k in d if k not in ("messages", "tools"))
        tc[f"{d.get('model')}|{json.dumps(d.get('tool_choice'))}"] += 1
        cap += any(k in d for k in ("max_tokens", "max_completion_tokens"))
        samp += any(k in d for k in ("temperature", "top_p", "top_k"))
    res = {"requests": n, "with_output_token_cap": cap, "with_sampling_parameter": samp,
           "top_level_keys": dict(keys), "tool_choice_by_model": dict(tc)}
    (OUT / "requests_census.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

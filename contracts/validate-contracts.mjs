import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const scriptPath = fileURLToPath(import.meta.url);
const contractsDir = path.dirname(scriptPath);
const repoRoot = path.resolve(contractsDir, "..");
const frontendDir = path.join(repoRoot, "frontend");
const schemasDir = path.join(contractsDir, "schemas");
const examplesDir = path.join(contractsDir, "examples");
const dataDir = path.join(contractsDir, "data");

const schemaFiles = [
  "state.schema.json",
  "event.schema.json",
  "action.schema.json",
  "decision.schema.json",
  "board.schema.json",
  "benchmark_artifact.schema.json",
  "failure_finding.schema.json",
  "research_registry.schema.json",
  "micro_scenario.schema.json",
  "micro_suite.schema.json",
  "micro_research.schema.json",
  "micro_result.schema.json"
];

async function resolveDependency(moduleId) {
  const candidates = [
    { label: "repo root", baseDir: repoRoot },
    { label: "frontend", baseDir: frontendDir }
  ];

  for (const candidate of candidates) {
    const packageJsonPath = path.join(candidate.baseDir, "package.json");
    try {
      await fs.access(packageJsonPath);
      const requireFrom = createRequire(packageJsonPath);
      return { path: requireFrom.resolve(moduleId), label: candidate.label };
    } catch (error) {
      continue;
    }
  }

  return null;
}

const ajvDependency = await resolveDependency("ajv/dist/2020.js");
const formatsDependency = await resolveDependency("ajv-formats");

if (!ajvDependency || !formatsDependency) {
  console.error("Missing dependencies for contract validation.");
  console.error("Fix (repo root): yarn");
  console.error("Fix (frontend only): cd frontend && yarn");
  process.exit(1);
}

const Ajv = (await import(pathToFileURL(ajvDependency.path).href)).default;
const addFormats = (await import(pathToFileURL(formatsDependency.path).href)).default;

async function loadSchemas() {
  const rawSchemas = await Promise.all(
    schemaFiles.map(async (fileName) => {
      const raw = await fs.readFile(path.join(schemasDir, fileName), "utf8");
      return JSON.parse(raw);
    })
  );

  const ajv = new Ajv({ allErrors: true, strict: false });
  addFormats(ajv);

  for (const schema of rawSchemas) {
    ajv.addSchema(schema);
  }

  return ajv;
}

function formatErrors(errors) {
  if (!errors || errors.length === 0) {
    return "unknown schema error";
  }
  return errors
    .map((error) => {
      const instancePath = error.instancePath || "/";
      return `${instancePath} ${error.message}`.trim();
    })
    .join("; ");
}

async function validateJsonExample(ajv, exampleFile, schemaId) {
  const raw = await fs.readFile(path.join(examplesDir, exampleFile), "utf8");
  const json = JSON.parse(raw);
  const validator = ajv.getSchema(schemaId);

  if (!validator) {
    throw new Error(`Schema not found for ${schemaId}`);
  }

  const valid = validator(json);
  if (!valid) {
    return { ok: false, error: formatErrors(validator.errors) };
  }

  return { ok: true };
}

async function validateJsonFile(ajv, filePath, schemaId) {
  const raw = await fs.readFile(filePath, "utf8");
  const json = JSON.parse(raw);
  const validator = ajv.getSchema(schemaId);

  if (!validator) {
    throw new Error(`Schema not found for ${schemaId}`);
  }

  const valid = validator(json);
  if (!valid) {
    return { ok: false, error: formatErrors(validator.errors) };
  }

  return { ok: true };
}

async function validateJsonlExample(ajv, exampleFile, schemaId) {
  const raw = await fs.readFile(path.join(examplesDir, exampleFile), "utf8");
  const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const validator = ajv.getSchema(schemaId);

  if (!validator) {
    throw new Error(`Schema not found for ${schemaId}`);
  }

  const failures = [];

  lines.forEach((line, index) => {
    let parsed;
    try {
      parsed = JSON.parse(line);
    } catch (error) {
      failures.push({
        line: index + 1,
        error: `invalid JSON: ${error.message}`
      });
      return;
    }

    const valid = validator(parsed);
    if (!valid) {
      failures.push({
        line: index + 1,
        error: formatErrors(validator.errors)
      });
    }
  });

  return { ok: failures.length === 0, failures, total: lines.length };
}

const ajv = await loadSchemas();
let failed = false;

const jsonExamples = [
  { file: "state.example.json", schema: "state.schema.json" },
  { file: "decision.example.json", schema: "decision.schema.json" },
  { file: "decision.jail.example.json", schema: "decision.schema.json" },
  { file: "decision.auction.example.json", schema: "decision.schema.json" },
  { file: "decision.post_turn.example.json", schema: "decision.schema.json" },
  { file: "decision.liquidation.example.json", schema: "decision.schema.json" },
  { file: "action.example.json", schema: "action.schema.json" },
  { file: "action.bid_auction.example.json", schema: "action.schema.json" },
  { file: "action.drop_out.example.json", schema: "action.schema.json" },
  { file: "artifact_manifest.example.json", schema: "benchmark_artifact.schema.json#/$defs/artifactManifest" },
  { file: "batch_config.example.json", schema: "benchmark_artifact.schema.json#/$defs/batchConfig" },
  { file: "model_card.example.json", schema: "benchmark_artifact.schema.json#/$defs/modelCard" },
  { file: "replay_step.example.json", schema: "benchmark_artifact.schema.json#/$defs/replayStep" },
  { file: "review_label.example.json", schema: "benchmark_artifact.schema.json#/$defs/reviewLabel" },
  { file: "trace_finding.example.json", schema: "benchmark_artifact.schema.json#/$defs/traceFinding" },
  { file: "failure_finding.example.json", schema: "failure_finding.schema.json" },
  { file: "research_seed_registry.example.json", schema: "research_registry.schema.json#/$defs/seedRegistry" },
  { file: "research_model_roster.example.json", schema: "research_registry.schema.json#/$defs/modelRosterRegistry" },
  { file: "long_campaign_config.example.json", schema: "research_registry.schema.json#/$defs/campaignConfig" },
  { file: "micro_expert_label_task.example.json", schema: "micro_research.schema.json#/$defs/expertLabelTask" },
  { file: "micro_expert_label.example.json", schema: "micro_research.schema.json#/$defs/expertLabel" }
];

for (const example of jsonExamples) {
  try {
    const result = await validateJsonExample(ajv, example.file, example.schema);
    if (result.ok) {
      console.log(`OK: ${example.file}`);
    } else {
      failed = true;
      console.error(`FAIL: ${example.file} -> ${result.error}`);
    }
  } catch (error) {
    failed = true;
    console.error(`FAIL: ${example.file} -> ${error.message}`);
  }
}

try {
  const boardPath = path.join(dataDir, "board.json");
  const result = await validateJsonFile(ajv, boardPath, "board.schema.json");
  if (result.ok) {
    console.log(`OK: data/board.json`);
  } else {
    failed = true;
    console.error(`FAIL: data/board.json -> ${result.error}`);
  }
} catch (error) {
  failed = true;
  console.error(`FAIL: data/board.json -> ${error.message}`);
}

try {
  const result = await validateJsonlExample(ajv, "event.example.jsonl", "event.schema.json");
  if (result.ok) {
    console.log(`OK: event.example.jsonl (${result.total}/${result.total})`);
  } else {
    failed = true;
    console.error(`FAIL: event.example.jsonl (${result.failures.length}/${result.total})`);
    for (const failure of result.failures) {
      console.error(`  line ${failure.line}: ${failure.error}`);
    }
  }
} catch (error) {
  failed = true;
  console.error(`FAIL: event.example.jsonl -> ${error.message}`);
}

const researchFiles = [
  { file: "monopoly_long_v1_seed_registry.json", schema: "research_registry.schema.json#/$defs/seedRegistry" },
  { file: "monopoly_long_v1_model_rosters.json", schema: "research_registry.schema.json#/$defs/modelRosterRegistry" }
];

for (const researchFile of researchFiles) {
  try {
    const researchPath = path.join(contractsDir, "research", researchFile.file);
    const result = await validateJsonFile(ajv, researchPath, researchFile.schema);
    if (result.ok) {
      console.log(`OK: research/${researchFile.file}`);
    } else {
      failed = true;
      console.error(`FAIL: research/${researchFile.file} -> ${result.error}`);
    }
  } catch (error) {
    failed = true;
    console.error(`FAIL: research/${researchFile.file} -> ${error.message}`);
  }
}

const campaignFiles = [
  { file: "monopoly-long-v1-smoke.json", schema: "research_registry.schema.json#/$defs/campaignConfig" }
];

for (const campaignFile of campaignFiles) {
  try {
    const campaignPath = path.join(repoRoot, "campaigns", campaignFile.file);
    const result = await validateJsonFile(ajv, campaignPath, campaignFile.schema);
    if (result.ok) {
      console.log(`OK: campaigns/${campaignFile.file}`);
    } else {
      failed = true;
      console.error(`FAIL: campaigns/${campaignFile.file} -> ${result.error}`);
    }
  } catch (error) {
    failed = true;
    console.error(`FAIL: campaigns/${campaignFile.file} -> ${error.message}`);
  }
}

async function validateMicroDirectory(directory, schemaId, label) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith(".json")) {
      continue;
    }
    const filePath = path.join(directory, entry.name);
    const result = await validateJsonFile(ajv, filePath, schemaId);
    if (result.ok) {
      console.log(`OK: ${label}/${entry.name}`);
    } else {
      failed = true;
      console.error(`FAIL: ${label}/${entry.name} -> ${result.error}`);
    }
  }
}

try {
  await validateMicroDirectory(
    path.join(contractsDir, "micro", "scenarios"),
    "micro_scenario.schema.json",
    "micro/scenarios"
  );
  await validateMicroDirectory(
    path.join(contractsDir, "micro", "suites"),
    "micro_suite.schema.json",
    "micro/suites"
  );
  await validateMicroDirectory(
    path.join(contractsDir, "micro", "research_suites"),
    "micro_research.schema.json#/$defs/microResearchSuite",
    "micro/research_suites"
  );
  await validateMicroDirectory(
    path.join(contractsDir, "micro", "counterfactual_pairs"),
    "micro_research.schema.json#/$defs/counterfactualPairRegistry",
    "micro/counterfactual_pairs"
  );
  await validateMicroDirectory(
    path.join(contractsDir, "micro", "campaigns"),
    "micro_research.schema.json#/$defs/microCampaignRegistry",
    "micro/campaigns"
  );
} catch (error) {
  failed = true;
  console.error(`FAIL: micro fixtures -> ${error.message}`);
}

if (failed) {
  process.exitCode = 1;
} else {
  console.log("All contract examples valid.");
}

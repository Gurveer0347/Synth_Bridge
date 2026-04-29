export const PIPELINE_STAGES = [
  {
    key: "reading",
    title: "Reading API Documentation",
    description: "ALI is analysing both API documentation files",
  },
  {
    key: "extracting",
    title: "Extracting Fields and Schema",
    description: "Identifying all available data fields in both tools",
  },
  {
    key: "mapping",
    title: "Mapping Fields Between Tools",
    description: "Figuring out which fields connect to which",
  },
  {
    key: "writing",
    title: "Writing Bridge Code",
    description: "Generating the Python connection script",
  },
  {
    key: "running",
    title: "Running and Delivering",
    description: "Executing the bridge and confirming delivery",
  },
];

const STAGE_INDEX = {
  ingesting: 0,
  reading: 0,
  extracting: 1,
  mapping: 2,
  generating: 3,
  writing: 3,
  running: 4,
  done: 4,
  failed: 4,
};

export function getStageIndex(stageName = "reading") {
  return STAGE_INDEX[stageName] ?? 0;
}

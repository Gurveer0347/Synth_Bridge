import { describe, expect, it } from "vitest";

import { PIPELINE_STAGES, getStageIndex } from "./pipeline";

describe("PIPELINE_STAGES", () => {
  it("matches the five-stage ALI roadmap sequence", () => {
    expect(PIPELINE_STAGES).toHaveLength(5);
    expect(PIPELINE_STAGES.map((stage) => stage.key)).toEqual([
      "reading",
      "extracting",
      "mapping",
      "writing",
      "running",
    ]);
    expect(PIPELINE_STAGES[0].title).toBe("Reading API Documentation");
    expect(PIPELINE_STAGES[4].description).toBe("Executing the bridge and confirming delivery");
  });
});

describe("getStageIndex", () => {
  it("converts backend and UI stage names into timeline indexes", () => {
    expect(getStageIndex("ingesting")).toBe(0);
    expect(getStageIndex("mapping")).toBe(2);
    expect(getStageIndex("generating")).toBe(3);
    expect(getStageIndex("running")).toBe(4);
    expect(getStageIndex("done")).toBe(4);
    expect(getStageIndex("failed")).toBe(4);
  });

  it("starts from the first stage for unknown stage names", () => {
    expect(getStageIndex("something-new")).toBe(0);
    expect(getStageIndex()).toBe(0);
  });
});

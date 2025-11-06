export const GVA_TRACKING_TYPES = [
  "zero-term",
  "short-term-imageless",
  "zero-term-imageless",
] as const;

export const gvaTrackConfig = {
  editableProperties: [
    {
      key: "tracking-type",
      label: "Tracking type",
      type: "select" as const,
      options: GVA_TRACKING_TYPES,
      defaultValue: "json",
      description:
        "Tracking algorithm used to identify the same object in multiple frames",
    },
  ],
};

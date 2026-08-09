# Architecture

Blocking generates a sparse candidate set using exact/domain keys. Feature extraction and conflict checks are pure functions; `Resolver` owns review memory, canonical mappings and provenance. Auto-match edges can be grouped only after checking all cross-component hard conflicts. Metrics evaluate pair decisions separately from resolution state, allowing thresholds to be compared without mutating mappings.

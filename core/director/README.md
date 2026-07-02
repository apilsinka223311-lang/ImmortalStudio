# Studio Director

Studio Director is the first orchestration layer of ImmortalStudio.

It does not generate stories, prompts, images, audio or video. Its job is to create a production task, load project context, validate the project structure and delegate the next stage through a pipeline interface.

The first downstream stage is Story Architect. If Story Architect has no executable implementation yet, Studio Director stops gracefully, saves `production_task.json`, writes logs and records:

```text
Waiting for Story Architect implementation.
```

This package is intentionally interface-driven so future agents can be plugged into the pipeline without rewriting Studio Director.

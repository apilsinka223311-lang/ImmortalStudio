\# ImmortalStudio



> Autonomous AI Animation Studio



\---



\# Vision



ImmortalStudio is an autonomous AI-powered animation studio designed to create entire animated series with minimal human involvement.



The long-term goal is simple:



One idea.



↓



One command.



↓



A complete animated episode.



The studio should eventually be capable of creating:



• YouTube Shorts

• 1–3 minute episodes

• Full animated series

• Complete seasons



without manual production.



\---



\# Mission



Build a production pipeline where specialized AI agents cooperate exactly like departments inside a real animation studio.



Every agent has one responsibility.



No agent performs work outside of its role.



\---



\# Core Principles



The studio is built around several principles.



\## Modular



Every subsystem can be replaced.



Gemini today.



Chinese models tomorrow.



No dependency should break the project.



\---



\## Autonomous



Human creates ideas.



Studio creates content.



\---



\## Persistent



Characters never forget.



World never resets.



Lore stays consistent.



\---



\## Scalable



One project.



Ten projects.



Hundreds of projects.



The architecture must support unlimited productions.



\---



\# Studio Architecture



```

Human



↓



Studio Director



↓



Story Architect



↓



Script Writer



↓



Prompt Engineer



↓



Image Director



↓



Animator



↓



Voice Director



↓



Music Director



↓



Video Editor



↓



Publisher



↓



Analytics

```



Every department works independently.



Communication happens only through defined files.



\---



\# Project Structure



```

ImmortalStudio/



agents/

core/

config/

docs/

docs/schemas/

memory/

output/

projects/

scripts/

assets/

plugins/

research/

tests/

tools/

```



\---



\# Projects



Every animated series is stored independently.



Example:



```

projects/



ImmortalAcademy/



PROJECT.md

README.md



world/

characters/

episodes/

production/

assets/

prompts/

```



Nothing inside one project affects another.



\---



\# Production Contracts



Agents communicate through documented file contracts.



The first canonical contracts are stored in:



```text

docs/schemas/

```



Current schema documents:



- `episode_plan.md`
- `episode_script.md`
- `scene_prompt.md`
- `character.md`
- `world.md`
- `metadata.md`



These contracts define what each agent produces, what the next agent consumes, and which fields must be validated before the pipeline continues.



\---



\# Codex Workflow



ImmortalStudio uses a repository-based one-task-per-run workflow for Codex development.



- `docs/TASK_QUEUE.md` defines the current queue and the first unchecked task.
- `reports/codex/` stores Russian implementation reports written after completed tasks.
- Codex must implement only one unchecked task per run, run relevant smoke tests, update the queue, write a report, and stop.



\---



\# AI Pipeline



Idea



↓



Story



↓



Episode Plan



↓



Script



↓



Scene Prompts



↓



Images



↓



Animation



↓



Voice



↓



Music



↓



Rendering



↓



Final Video



↓



Publishing



↓



Analytics



\---



\# Memory System



The studio remembers:



• Characters



• World



• Relationships



• Timeline



• Episodes



• Prompts



• Voice settings



• Visual style



Nothing important should ever be regenerated from scratch.

Preferred project memory layout is documented in:

- `docs/PROJECT_MEMORY_LAYOUT.md`



\---



\# Long-Term Goal



The final version of ImmortalStudio should allow:



```

Create Series



↓



Generate Entire Season



↓



Render Episodes



↓



Upload to YouTube



↓



Collect Analytics



↓



Improve Future Episodes



↓



Repeat Forever

```



\---



\# Technology



The system is designed to work with multiple AI providers.



Possible integrations:



• Gemini

• Claude

• OpenAI

• Qwen

• GLM

• DeepSeek

• ComfyUI

• Wan

• Hailuo

• MiniMax

• Kokoro TTS

• Fish Speech

• XTTS

• Whisper



The architecture must remain provider-independent.



\---



\# Repository Philosophy



This repository is not just source code.



It is the operating system of an autonomous AI animation studio.



Every file, document, script, and agent exists to move one step closer to fully automated content creation.



\---



Version



Foundation v0.1


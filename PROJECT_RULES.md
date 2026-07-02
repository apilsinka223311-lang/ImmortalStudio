\# ImmortalStudio Development Rules



Version: Foundation v0.1



\---



\# Purpose



This document defines the mandatory rules for developing ImmortalStudio.



Every human developer and every AI agent must follow these rules.



These rules have higher priority than convenience.



\---



\# Core Philosophy



ImmortalStudio is not a collection of scripts.



It is an operating system for autonomous AI animation production.



Every decision must move the project closer to full automation.



\---



\# General Rules



\## Rule 1



Never sacrifice long-term architecture for short-term convenience.



\---



\## Rule 2



Documentation comes before implementation.



Every important system must be documented before code is written.



\---



\## Rule 3



Every component has exactly one responsibility.



Avoid multi-purpose modules.



\---



\## Rule 4



Everything must be replaceable.



Changing an AI provider must never require rewriting the entire project.



\---



\## Rule 5



Every project is isolated.



Series never share memory.



Series never overwrite each other.



\---



\## Rule 6



No hardcoded values unless absolutely necessary.



Configuration belongs inside config/.



\---



\## Rule 7



Never duplicate information.



Reuse existing memory whenever possible.



\---



\## Rule 8



Every generated asset must be reproducible.



Prompts, seeds, settings and versions must be stored.



\---



\# AI Rules



Every AI agent has exactly one responsibility.



Agents communicate only through project files.



Agents must never modify files outside their assigned responsibility unless explicitly instructed.



Agents should improve existing work instead of recreating it.



Whenever possible, agents should preserve continuity.



\---



\# Documentation Rules



Every major system requires documentation.



Documentation should explain:



Purpose



Inputs



Outputs



Dependencies



Limitations



Future improvements



\---



\# Memory Rules



Nothing important should exist only inside prompts.



Everything important must be stored.



Memory includes:



Characters



World



Relationships



Episode history



Visual references



Prompt templates



Voice settings



Lore



Timeline



Style



\---



\# Coding Rules



Readable code is more important than clever code.



Small modules are preferred.



Reusable functions are preferred.



Avoid unnecessary dependencies.



Prefer explicit logic over hidden behavior.



Document non-obvious decisions.



\---



\# Project Rules



Every animated series has its own project folder.



Every project contains:



PROJECT.md



README.md



world/



characters/



episodes/



production/



assets/



prompts/



Projects must never interfere with one another.



\---



\# Automation Rules



Every manual step should eventually become automated.



If a task is repeated multiple times, it should become a future feature.



\---



\# Quality Rules



Never optimize before correctness.



Never automate broken workflows.



Never introduce complexity without measurable benefit.



Every improvement must make the studio more reliable.



\---



\# AI Provider Rules



The architecture must remain provider-independent.



No component should depend on a single vendor.



Replacing one AI model should require minimal changes.



\---



\# Git Rules



Commit frequently.



Write meaningful commit messages.



Never commit secrets.



Never commit API keys.



Never commit generated cache.



\---



\# Security Rules



API keys belong only in local configuration.



Secrets are never stored inside the repository.



Sensitive data must remain outside version control.



\---



\# Future Rule



Whenever a new feature is proposed, ask one question:



"Does this move ImmortalStudio closer to autonomous production?"



If the answer is no, reconsider implementing it.



\---



\# Final Principle



Everything inside this repository exists for one purpose:



Build the world's first fully autonomous AI animation studio.


# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- Primary: NEU students learning introductory Python who use course spaces, assignments, the coding IDE, and the AI tutor.
- Secondary: instructors who manage courses, assignments, learning progress, and exam/practice sessions.

## Product Purpose

PyTutor-MCP is a university learning platform that combines course management, a Python practice IDE, and an adaptive AI tutor. Success means students can practice and understand programming tasks while instructors can organize coursework and review class progress.

## Positioning

The tutor is grounded in the student's code, execution/test results, and learning context exposed through the project's MCP tools; it is designed to guide rather than simply provide complete answers.

## Operating Context

Students sign in, enter a course or practice space, write and run Python, ask for hints, and submit solutions. Instructors sign in to manage classes and exercises, review progress, and configure academic sessions. The web application uses React, Vite, and Tailwind CSS and communicates with a FastAPI backend.

## Capabilities and Constraints

- Preserve existing authentication, demo sign-in, role-based navigation, class/course flows, submission actions, exam restrictions, and session identity.
- The product includes separate student and instructor experiences, a multi-panel coding workspace, and an AI tutor.
- UI work must not change API calls or academic/business rules.
- The interface language is Vietnamese, with programming terms where appropriate.

## Brand Commitments

- Product name: PyTutor-MCP.
- Use clear, supportive educational language; the tutor should encourage independent problem solving.

## Evidence on Hand

- The repository contains the existing React frontend, course and IDE workflows, and `AI_HANDOFF_CONTEXT.md` / `PLAN.md` describing current product behavior.
- Do not invent institutional endorsements, learning-outcome statistics, or other proof claims.

## Product Principles

- Protect academic integrity and student autonomy.
- Keep course, role, and exam context clear.
- Make the next learning action easy to understand.
- Preserve existing workflows when improving presentation.

## Accessibility & Inclusion

Interactive controls need keyboard focus visibility and accessible names; error, loading, and disabled states must be understandable without relying on color alone.

# CLAUDE.md - AI Assistant Guide for auto2tesst

This document serves as a comprehensive guide for AI assistants (like Claude) working on the `auto2tesst` repository. It provides critical context about the codebase structure, development workflows, and conventions to follow.

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflow](#development-workflow)
4. [Key Conventions](#key-conventions)
5. [Testing Guidelines](#testing-guidelines)
6. [Git Workflow](#git-workflow)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Repository Overview

**Repository**: auto2tesst
**Status**: Initial setup phase
**Primary Language**: TBD
**Framework/Stack**: TBD

### Purpose

This repository is currently in its initial setup phase. This section should be updated to describe:
- The main purpose and goals of the project
- Target users or use cases
- Key features and functionality
- Any unique aspects or requirements

---

## Codebase Structure

Currently, the repository is empty. As the project develops, document the directory structure here:

```
auto2tesst/
├── .git/               # Git version control
└── CLAUDE.md           # This file
```

### Expected Structure (to be updated as project grows)

When adding code, consider organizing by:
- **Source code**: Main application/library code
- **Tests**: Unit, integration, and end-to-end tests
- **Configuration**: Environment configs, build configs
- **Documentation**: Additional docs beyond this file
- **Scripts**: Build, deployment, or utility scripts
- **Assets**: Static files, images, data files

---

## Development Workflow

### Setting Up Development Environment

As the project develops, document:
1. Prerequisites (languages, tools, versions)
2. Installation steps
3. Environment configuration
4. Initial setup commands

### Running the Project

Document how to:
- Start the development server/application
- Build for production
- Run in different environments

---

## Key Conventions

### Code Style

Define and document:
- **Formatting**: Indentation (spaces/tabs), line length
- **Naming**: Variables, functions, classes, files
- **Comments**: When and how to comment
- **Language-specific**: Framework patterns, idioms

### File Organization

- How files should be named
- Where different types of files should live
- Module/component organization patterns

### Dependencies

- How to add new dependencies
- Version pinning strategy
- Dependency update policy

---

## Testing Guidelines

### Testing Strategy

Document the testing approach:
- **Unit Tests**: What to test, coverage expectations
- **Integration Tests**: Component interaction testing
- **E2E Tests**: User flow testing
- **Test Location**: Where tests should be placed

### Running Tests

Commands and procedures for:
- Running all tests
- Running specific test suites
- Running tests in watch mode
- Generating coverage reports

### Writing Tests

- Test naming conventions
- Test structure patterns
- Mocking/stubbing guidelines
- Test data management

---

## Git Workflow

### Branch Strategy

**Feature Branch Workflow**:
- Main/master branch: Production-ready code
- Feature branches: Named `claude/<description>-<session-id>`
- Development branches: As specified per task

### Commit Guidelines

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Best Practices**:
- Keep commits atomic and focused
- Write clear, descriptive commit messages
- Reference issues/PRs when relevant
- Avoid committing sensitive data (.env files, credentials)

### Push Protocol

When pushing changes:
1. Review changes with `git status` and `git diff`
2. Stage relevant files
3. Commit with descriptive message
4. Push to feature branch: `git push -u origin <branch-name>`
5. Retry with exponential backoff if network errors occur

---

## Common Tasks

### Adding a New Feature

1. Create/checkout feature branch
2. Implement the feature with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Commit changes
6. Push to remote branch
7. Create pull request (if applicable)

### Fixing a Bug

1. Identify and reproduce the bug
2. Write a failing test that demonstrates the bug
3. Fix the bug
4. Ensure the test passes
5. Ensure all other tests still pass
6. Commit and push

### Updating Dependencies

1. Check for outdated dependencies
2. Review changelogs for breaking changes
3. Update dependency versions
4. Run full test suite
5. Update documentation if APIs changed
6. Commit changes

### Refactoring

1. Ensure comprehensive test coverage exists
2. Make incremental changes
3. Run tests after each change
4. Keep commits small and focused
5. Document any API changes

---

## Troubleshooting

### Common Issues

This section will be populated as common issues arise. Document:
- Issue description
- Root cause
- Solution/workaround
- Prevention strategies

### Debug Strategies

When investigating issues:
1. Reproduce the problem consistently
2. Isolate the failing component
3. Check recent changes (git log, git diff)
4. Review relevant logs
5. Add debug logging if needed
6. Test fixes incrementally

---

## AI Assistant Specific Guidelines

### Code Analysis

When analyzing this codebase:
1. Use the Explore agent for comprehensive codebase exploration
2. Use Grep for targeted searches within known areas
3. Use Glob for finding files by pattern
4. Read relevant documentation files first

### Task Planning

For complex tasks:
1. Use TodoWrite to plan and track progress
2. Break down large tasks into smaller steps
3. Mark todos as in_progress before starting
4. Mark todos as completed immediately after finishing
5. Keep only one todo in_progress at a time

### Code Modifications

When modifying code:
1. Always read files before editing
2. Prefer Edit tool over Write for existing files
3. Maintain existing code style and patterns
4. Add tests for new functionality
5. Run tests before committing
6. Never commit files with secrets or credentials

### Security Considerations

Always consider:
- Input validation and sanitization
- SQL injection prevention
- XSS prevention
- CSRF protection
- Authentication and authorization
- Secure credential handling
- OWASP Top 10 vulnerabilities

---

## Project Evolution

As this project grows, update this document to reflect:
- New architectural decisions
- Technology stack choices
- Design patterns adopted
- Integration patterns
- Deployment procedures
- Monitoring and logging approaches
- Performance optimization strategies

---

## Notes for AI Assistants

### Communication Style

- Be concise and direct
- Use technical accuracy over validation
- Avoid emojis unless explicitly requested
- Focus on problem-solving
- Provide objective guidance

### Tool Usage

- Prefer specialized tools over bash commands for file operations
- Run independent operations in parallel when possible
- Use Task tool for complex, multi-step operations
- Use appropriate agents (Explore, Plan) for their specialized purposes

### Best Practices

- Always verify file paths before operations
- Check for existing patterns before introducing new ones
- Consider backward compatibility
- Document significant decisions
- Test thoroughly before committing
- Ask for clarification when requirements are ambiguous

---

## Maintenance

**Last Updated**: 2025-11-15
**Updated By**: Claude (Initial creation)

**Update Triggers**:
- Major architectural changes
- New technology adoption
- Significant workflow changes
- Common issues discovered
- New team conventions established

---

## Additional Resources

As the project develops, add links to:
- External documentation
- API references
- Design documents
- Architecture diagrams
- Related repositories
- Issue tracker
- CI/CD pipeline

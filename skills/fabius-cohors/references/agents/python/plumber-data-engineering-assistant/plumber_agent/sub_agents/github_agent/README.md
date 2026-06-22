# GitHub Agent

AI-powered agent for GitHub repository management and Git operations using Google's Agent Development Kit (ADK).


## Tools Overview

### GitHub Tools
| Tool | Purpose |
|------|---------|
| [`authenticate_github`](tools/github_api.py) | Verify GitHub API authentication |
| [`search_repositories`](tools/github_api.py) | Search GitHub repositories by keywords |
| [`list_branches`](tools/github_api.py) | List all branches in a repository |
| [`download_repository`](tools/github_api.py) | Download repository to local storage |

### Git Tools
| Tool | Purpose |
|------|---------|
| [`initialize_git_repo`](tools/git_ops.py) | Initialize new Git repository |
| [`get_git_status`](tools/git_ops.py) | Check repository status and changes |
| [`add_files_to_git`](tools/git_ops.py) | Stage files for commit |
| [`commit_changes`](tools/git_ops.py) | Create commits with messages |
| [`list_git_branches`](tools/git_ops.py) | List all local branches |
| [`switch_git_branch`](tools/git_ops.py) | Switch or create branches |

## Key Features

- 🔐 Secure GitHub authentication
- 📦 Repository download and management  
- 🌿 Branch operations and Git workflow
- 🤖 AI-powered with Google ADK


## Support

- [Google ADK Docs](https://developers.google.com/adk)
- [GitHub API Docs](https://docs.github.com/en/rest)
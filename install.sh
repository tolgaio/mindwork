#!/bin/sh
# Mindwork Plugin Installation Script
# Creates symlinks from ~/.claude/ to the plugin directory
#
# Usage:
#   ./install.sh              Install skills to ~/.claude/skills/
#   ./install.sh --uninstall  Remove installed symlinks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located (plugin root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_NAME="mindwork"

# Target directories
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
COMMANDS_DIR="$CLAUDE_DIR/commands"
AGENTS_DIR="$CLAUDE_DIR/agents"

print_status() {
    printf "${BLUE}[*]${NC} %s\n" "$1"
}

print_success() {
    printf "${GREEN}[+]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[!]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[-]${NC} %s\n" "$1"
}

install_skills() {
    # Check if skills directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/skills" ]; then
        print_warning "No skills directory found in plugin"
        return
    fi

    print_status "Installing skills..."

    # Create skills directory if it doesn't exist
    if [ ! -d "$SKILLS_DIR" ]; then
        mkdir -p "$SKILLS_DIR"
        print_success "Created $SKILLS_DIR"
    fi

    # Create symlink for each skill
    for skill_path in "$SCRIPT_DIR/skills"/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")
            target="$SKILLS_DIR/$skill_name"

            # Remove existing symlink or directory
            if [ -L "$target" ]; then
                rm "$target"
            elif [ -d "$target" ]; then
                print_error "Cannot install $skill_name: $target exists and is not a symlink"
                continue
            fi

            # Create symlink
            ln -s "$skill_path" "$target"
            print_success "Linked: $skill_name"
        fi
    done
}

install_commands() {
    # Check if commands directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/commands" ]; then
        return
    fi

    print_status "Installing commands..."

    # Create commands directory if it doesn't exist
    if [ ! -d "$COMMANDS_DIR" ]; then
        mkdir -p "$COMMANDS_DIR"
        print_success "Created $COMMANDS_DIR"
    fi

    # Create symlink for each command
    for cmd_path in "$SCRIPT_DIR/commands"/*.md; do
        if [ -f "$cmd_path" ]; then
            cmd_name=$(basename "$cmd_path")
            target="$COMMANDS_DIR/$cmd_name"

            # Remove existing symlink
            if [ -L "$target" ]; then
                rm "$target"
            elif [ -f "$target" ]; then
                print_error "Cannot install $cmd_name: $target exists and is not a symlink"
                continue
            fi

            # Create symlink
            ln -s "$cmd_path" "$target"
            print_success "Linked: $cmd_name"
        fi
    done
}

install_agents() {
    # Check if agents directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/agents" ]; then
        return
    fi

    print_status "Installing agents..."

    # Create agents directory if it doesn't exist
    if [ ! -d "$AGENTS_DIR" ]; then
        mkdir -p "$AGENTS_DIR"
        print_success "Created $AGENTS_DIR"
    fi

    # Create symlink for each agent
    for agent_path in "$SCRIPT_DIR/agents"/*.md; do
        if [ -f "$agent_path" ]; then
            agent_name=$(basename "$agent_path")
            target="$AGENTS_DIR/$agent_name"

            # Remove existing symlink
            if [ -L "$target" ]; then
                rm "$target"
            elif [ -f "$target" ]; then
                print_error "Cannot install $agent_name: $target exists and is not a symlink"
                continue
            fi

            # Create symlink
            ln -s "$agent_path" "$target"
            print_success "Linked: $agent_name"
        fi
    done
}

uninstall() {
    print_status "Uninstalling ${PLUGIN_NAME} plugin..."

    # Remove skill symlinks
    if [ -d "$SKILLS_DIR" ]; then
        for target in "$SKILLS_DIR/${PLUGIN_NAME}-"*; do
            if [ -L "$target" ]; then
                rm "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    # Remove command symlinks
    if [ -d "$COMMANDS_DIR" ]; then
        for target in "$COMMANDS_DIR/${PLUGIN_NAME}-"*.md; do
            if [ -L "$target" ]; then
                rm "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    # Remove agent symlinks
    if [ -d "$AGENTS_DIR" ]; then
        for target in "$AGENTS_DIR/${PLUGIN_NAME}-"*.md; do
            if [ -L "$target" ]; then
                rm "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    print_success "Uninstallation complete!"
}

install() {
    print_status "Installing ${PLUGIN_NAME} plugin..."
    print_status "Plugin location: $SCRIPT_DIR"
    echo ""

    install_skills
    install_commands
    install_agents

    echo ""
    print_success "Installation complete!"
    echo ""
    print_status "Skills are symlinked - changes to source files are reflected immediately."
    print_status "Restart Claude Code to use the new skills:"
    echo "  - mindwork-analyze"
    echo "  - mindwork-insights"
    echo "  - mindwork-progress"
    echo "  - mindwork-summary"
    echo "  - mindwork-transcribe"
}

# Main
case "${1:-}" in
    --uninstall|-u)
        uninstall
        ;;
    --help|-h)
        echo "Mindwork Plugin Installation Script"
        echo ""
        echo "Usage:"
        echo "  ./install.sh              Install skills via symlinks to ~/.claude/"
        echo "  ./install.sh --uninstall  Remove installed symlinks"
        echo "  ./install.sh --help       Show this help"
        echo ""
        echo "This script creates symlinks from ~/.claude/skills/ to the plugin directory."
        echo "Changes to source files are reflected immediately without re-running install."
        ;;
    "")
        install
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

#!/bin/bash

# install chezmoi

if ! [ -x "$(command -v chezmoi)" ] ; then
    curl -sfL https://git.io/chezmoi | bash -s -- -d -b ~/.bin
fi

PATH=~/.bin:$PATH
chezmoi init https://github.com/overdrive3000/rcs.git
chezmoi diff

COMPLETION_DST="$HOME/.oh-my-zsh/completions"
mkdir -p "$COMPLETION_DST"
chezmoi completion zsh > "$COMPLETION_DST/_chezmoi" 

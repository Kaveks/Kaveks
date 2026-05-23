GITHUB_USERNAME ?= kaveks
GH_TOKEN       ?=
BRANCH         ?= main

.PHONY: install generate all push sync

all: install generate

install:
	pip install -r requirements.txt

generate:
	python3 generate_contributions.py $(GITHUB_USERNAME) $(GH_TOKEN)

push:
	git pull --rebase origin $(BRANCH)
	git push -u origin $(BRANCH)

sync: generate push

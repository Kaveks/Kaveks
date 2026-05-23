GITHUB_USERNAME ?= kaveks
GH_TOKEN       ?=

.PHONY: install generate all

all: install generate

install:
	pip install -r requirements.txt

generate:
	python3 generate_contributions.py $(GITHUB_USERNAME) $(GH_TOKEN)

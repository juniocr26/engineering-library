# Evidence record: revision-signals-current-evaluation.json

This is a dated raw research artifact. Findings and rejected model outputs retain their recorded status. Reading the record does not approve publication or training.

SHA-256: `e1ec4a6b8242574bfcb0b2e1a48965fa1534fefc85b80e39fbe00a862dad590f`. Original bytes: `21224`.

Original path: `agent/research/documentation-intelligence-20261119/revision-signals-current-evaluation.json`.

<!-- reading-section:reference:e1ec4a6b8242574bfcb0:consumers -->
## Referenced by

- [Documentation agent: source, identity and ownership contracts](../chapters/documentation-agent-contracts.md)

<!-- reading-section:reference:e1ec4a6b8242574bfcb0:artifact -->
## Original artifact

The fenced contents reproduce the exact UTF-8 artifact; a display-only terminal newline is added if the original lacks one.

<!-- artifact-body:e1ec4a6b8242574bfcb0b2e1a48965fa1534fefc85b80e39fbe00a862dad590f:start -->
````json
{
  "at": "2026-11-20T05:36:10.650172+00:00",
  "status": "PASSED_CURRENT_STRUCTURAL_REAL_REVISION_REGRESSION",
  "version": "0.1.1",
  "protocol_sha256": "ae62bf6c610d0e22b0b57a2ecf5f0e6b0d3b1f926261a100f1a5b5e0dcca6f00",
  "cases": 5,
  "signal_matches": 5,
  "manual_actions_not_automated": {
    "MODIFY": 2,
    "ADD": 1,
    "NO-OP": 2
  },
  "documentation_actions_selected": 0,
  "existing_lifecycle_abstentions_preserved": 5,
  "results": [
    {
      "path": "src/cachetools/__init__.py",
      "result": {
        "version": "0.1.1",
        "status": "STRUCTURAL_REVISION_OBSERVATIONS",
        "documentation_action": null,
        "source_executed": false,
        "runtime_bindings_verified": false,
        "owner_approved": false,
        "publication_authorized": false,
        "training_gold": false,
        "model_calls": 0,
        "writes": 0,
        "implementation": {
          "version": "0.1.1",
          "implementation_sha256": "53a233c43eab81ce3bcf113a102cdcf704702fdf36d32c4babe479116e28b525",
          "retrieval_sha256": "afc77b34d46d95f3ec251ac837ce91495f7b2518cd98e80e1305c5c19339030c",
          "workspace_sha256": "0bfc4c447c999eda21bbb580e2a3d9d808e90b59b09c1ac8f6025482f3dc0604",
          "python_version": "3.14.7 (main, Aug  5 2026, 10:29:49) [Clang 21.0.0 (clang-2100.1.1.101)]"
        },
        "source_cards": {
          "previous": {
            "path": "src/cachetools/__init__.py",
            "revision": "1fcadea96ce67d499965b085f0b0b2253b78bb80",
            "sha256": "0d73ca9095017dfdd65bcb9f1d2f13539dde3b3959eb0197f865cd007d07bdd9"
          },
          "current": {
            "path": "src/cachetools/__init__.py",
            "revision": "c403f9f4185e58090b904c1915345b9ba46d5a08",
            "sha256": "72eb5453a7c1d5b20c8a1d2ba3f4d508f2894cfc0cfaa3f87d2fcfc8d7d0956b"
          }
        },
        "observations": {
          "current_module_ast_sha256": "d8b160b248c2e42b72777a859c9c287097073138db0399e66ba5401893d6d2d4",
          "module_signal": "DIFFERENT_WRITTEN_MODULE_AST",
          "observations": [
            {
              "current": {
                "declaration_ast_sha256": "3e8d90c90e5530631e64b57e5156d2094589e8216439e776ae9039503e12fcc0",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 470,
                  "last_line": 490,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "    def expire(self, time=None):\n        \"\"\"Remove expired items from the cache and return an iterable of the\n        expired `(key, value)` pairs.\n\n        \"\"\"\n        if time is None:\n            time = self.timer()\n        root = self.__root\n        curr = root.next\n        links = self.__links\n        expired = []\n        cache_delitem = Cache.__delitem__\n        cache_getitem = Cache.__getitem__\n        while curr is not root and not (time < curr.expires):\n            expired.append((curr.key, cache_getitem(self, curr.key)))\n            cache_delitem(self, curr.key)\n            del links[curr.key]\n            next = curr.next\n            curr.unlink()\n            curr = next\n        return expired\n",
                  "quote_byte_end": 14016,
                  "quote_byte_start": 13304,
                  "quote_sha256": "3ac39353b5b61b94e9a5bd34090615f7214ed8c66fb39d2c297afa427e49cba3",
                  "runtime_bindings_verified": false,
                  "selector": "TTLCache.expire",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "TTLCache.expire",
                "status": "DECLARATION_ESTABLISHED"
              },
              "enclosing_module_changed": true,
              "previous": {
                "declaration_ast_sha256": "d24822f177155750ac1c5e1f640918e20f99f34d5e9951be6ba20d8287fcf681",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 467,
                  "last_line": 480,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "    def expire(self, time=None):\n        \"\"\"Remove expired items from the cache.\"\"\"\n        if time is None:\n            time = self.timer()\n        root = self.__root\n        curr = root.next\n        links = self.__links\n        cache_delitem = Cache.__delitem__\n        while curr is not root and not (time < curr.expires):\n            cache_delitem(self, curr.key)\n            del links[curr.key]\n            next = curr.next\n            curr.unlink()\n            curr = next\n",
                  "quote_byte_end": 13635,
                  "quote_byte_start": 13156,
                  "quote_sha256": "5c72988183a9bdd1ce9a6d1f5a7d04e238756ff44aa0068183b860660b7a0a82",
                  "runtime_bindings_verified": false,
                  "selector": "TTLCache.expire",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "TTLCache.expire",
                "status": "DECLARATION_ESTABLISHED"
              },
              "selector": "TTLCache.expire",
              "signal": "DIFFERENT_WRITTEN_DECLARATION_AST",
              "unchanged_selection_requires_dependency_review": false
            },
            {
              "current": {
                "declaration_ast_sha256": "a6bdf63aa06048118efcda51aee5e4bfa3298cf55d95c31e7d3e5988b5942ca6",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 590,
                  "last_line": 612,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "    def expire(self, time=None):\n        \"\"\"Remove expired items from the cache and return an iterable of the\n        expired `(key, value)` pairs.\n\n        \"\"\"\n        if time is None:\n            time = self.timer()\n        items = self.__items\n        order = self.__order\n        # clean up the heap if too many items are marked as removed\n        if len(order) > len(items) * 2:\n            self.__order = order = [item for item in order if not item.removed]\n            heapq.heapify(order)\n        expired = []\n        cache_delitem = Cache.__delitem__\n        cache_getitem = Cache.__getitem__\n        while order and (order[0].removed or not (time < order[0].expires)):\n            item = heapq.heappop(order)\n            if not item.removed:\n                expired.append((item.key, cache_getitem(self, item.key)))\n                cache_delitem(self, item.key)\n                del items[item.key]\n        return expired\n",
                  "quote_byte_end": 18113,
                  "quote_byte_start": 17182,
                  "quote_sha256": "62cda0998164c5d0c05fe849c8b9d83898dab64bfadc31c9a860e04e2b031193",
                  "runtime_bindings_verified": false,
                  "selector": "TLRUCache.expire",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "TLRUCache.expire",
                "status": "DECLARATION_ESTABLISHED"
              },
              "enclosing_module_changed": true,
              "previous": {
                "declaration_ast_sha256": "4ac8f089850224050837b60a0024be06088683d2a9209b207136387fb34b60c9",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 581,
                  "last_line": 596,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "    def expire(self, time=None):\n        \"\"\"Remove expired items from the cache.\"\"\"\n        if time is None:\n            time = self.timer()\n        items = self.__items\n        order = self.__order\n        # clean up the heap if too many items are marked as removed\n        if len(order) > len(items) * 2:\n            self.__order = order = [item for item in order if not item.removed]\n            heapq.heapify(order)\n        cache_delitem = Cache.__delitem__\n        while order and (order[0].removed or not (time < order[0].expires)):\n            item = heapq.heappop(order)\n            if not item.removed:\n                cache_delitem(self, item.key)\n                del items[item.key]\n",
                  "quote_byte_end": 17496,
                  "quote_byte_start": 16802,
                  "quote_sha256": "04d7d4a5d7f878593027f6c148c0b27059ce66e396d9801f42d24a62474538d1",
                  "runtime_bindings_verified": false,
                  "selector": "TLRUCache.expire",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "TLRUCache.expire",
                "status": "DECLARATION_ESTABLISHED"
              },
              "selector": "TLRUCache.expire",
              "signal": "DIFFERENT_WRITTEN_DECLARATION_AST",
              "unchanged_selection_requires_dependency_review": false
            }
          ],
          "previous_module_ast_sha256": "5cae4cc76fbefbac52a4cc262450a9182aa9f18befe00d333a036eb6f44e401d",
          "quote_bytes": 2816
        },
        "evidence_key": "30938c4abbb6ff052b47a4035507bece5b16707e8b8d53de661015a117827589",
        "limitations": [
          "Written AST equality is not runtime behavior, dependency completeness or permission to skip a document review.",
          "Source cards are operator-supplied snapshots, not proof of current filesystem state or authenticated repository origin.",
          "Missing or ambiguous selection is never retirement evidence. No documentation action is chosen."
        ]
      }
    },
    {
      "path": "src/cachetools/keys.py",
      "result": {
        "version": "0.1.1",
        "status": "STRUCTURAL_REVISION_OBSERVATIONS",
        "documentation_action": null,
        "source_executed": false,
        "runtime_bindings_verified": false,
        "owner_approved": false,
        "publication_authorized": false,
        "training_gold": false,
        "model_calls": 0,
        "writes": 0,
        "implementation": {
          "version": "0.1.1",
          "implementation_sha256": "53a233c43eab81ce3bcf113a102cdcf704702fdf36d32c4babe479116e28b525",
          "retrieval_sha256": "afc77b34d46d95f3ec251ac837ce91495f7b2518cd98e80e1305c5c19339030c",
          "workspace_sha256": "0bfc4c447c999eda21bbb580e2a3d9d808e90b59b09c1ac8f6025482f3dc0604",
          "python_version": "3.14.7 (main, Aug  5 2026, 10:29:49) [Clang 21.0.0 (clang-2100.1.1.101)]"
        },
        "source_cards": {
          "previous": {
            "path": "src/cachetools/keys.py",
            "revision": "1fcadea96ce67d499965b085f0b0b2253b78bb80",
            "sha256": "77e7295b6e7613fb95e74c92970d7721ebdd3509d273431f88c562226424b512"
          },
          "current": {
            "path": "src/cachetools/keys.py",
            "revision": "c403f9f4185e58090b904c1915345b9ba46d5a08",
            "sha256": "00e81fa22fa88a804e9c4124d75e7ff6ab341ca212ad89db715e05d21c99d729"
          }
        },
        "observations": {
          "current_module_ast_sha256": "dbfd08ed79051a461977298083d067772521aa890159bb7cbe420d34cadf7a6a",
          "module_signal": "DIFFERENT_WRITTEN_MODULE_AST",
          "observations": [
            {
              "current": {
                "declaration_ast_sha256": "44f3288afd58505afc564de5104e6c6f0868ec4d2fdb4bef6df51ee903b8c458",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 46,
                  "last_line": 48,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "def methodkey(self, *args, **kwargs):\n    \"\"\"Return a cache key for use with cached methods.\"\"\"\n    return hashkey(*args, **kwargs)\n",
                  "quote_byte_end": 1373,
                  "quote_byte_start": 1241,
                  "quote_sha256": "76b2f4bf4a9dc67c99a1ad0452176dde1ef184763f41315780d77b8be02cea07",
                  "runtime_bindings_verified": false,
                  "selector": "methodkey",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "methodkey",
                "status": "DECLARATION_ESTABLISHED"
              },
              "enclosing_module_changed": true,
              "previous": {
                "declaration_ast_sha256": "44f3288afd58505afc564de5104e6c6f0868ec4d2fdb4bef6df51ee903b8c458",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 46,
                  "last_line": 48,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "def methodkey(self, *args, **kwargs):\n    \"\"\"Return a cache key for use with cached methods.\"\"\"\n    return hashkey(*args, **kwargs)\n",
                  "quote_byte_end": 1355,
                  "quote_byte_start": 1223,
                  "quote_sha256": "76b2f4bf4a9dc67c99a1ad0452176dde1ef184763f41315780d77b8be02cea07",
                  "runtime_bindings_verified": false,
                  "selector": "methodkey",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "methodkey",
                "status": "DECLARATION_ESTABLISHED"
              },
              "selector": "methodkey",
              "signal": "IDENTICAL_WRITTEN_DECLARATION_AST",
              "unchanged_selection_requires_dependency_review": true
            },
            {
              "current": {
                "declaration_ast_sha256": "f41a4fdf6592d8e52a5a3cf364dfd46a92352e43828cd93cea4defcde9fb2341",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 37,
                  "last_line": 43,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "def hashkey(*args, **kwargs):\n    \"\"\"Return a cache key for the specified hashable arguments.\"\"\"\n\n    if kwargs:\n        return _HashedTuple(args + sum(sorted(kwargs.items()), _kwmark))\n    else:\n        return _HashedTuple(args)\n",
                  "quote_byte_end": 1239,
                  "quote_byte_start": 1009,
                  "quote_sha256": "6041b7e0cceeca3923bbc884117e963f8583fe384a0f6c033713c63738c50b61",
                  "runtime_bindings_verified": false,
                  "selector": "hashkey",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "hashkey",
                "status": "DECLARATION_ESTABLISHED"
              },
              "enclosing_module_changed": true,
              "previous": {
                "declaration_ast_sha256": "f41a4fdf6592d8e52a5a3cf364dfd46a92352e43828cd93cea4defcde9fb2341",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 37,
                  "last_line": 43,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "def hashkey(*args, **kwargs):\n    \"\"\"Return a cache key for the specified hashable arguments.\"\"\"\n\n    if kwargs:\n        return _HashedTuple(args + sum(sorted(kwargs.items()), _kwmark))\n    else:\n        return _HashedTuple(args)\n",
                  "quote_byte_end": 1221,
                  "quote_byte_start": 991,
                  "quote_sha256": "6041b7e0cceeca3923bbc884117e963f8583fe384a0f6c033713c63738c50b61",
                  "runtime_bindings_verified": false,
                  "selector": "hashkey",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "hashkey",
                "status": "DECLARATION_ESTABLISHED"
              },
              "selector": "hashkey",
              "signal": "IDENTICAL_WRITTEN_DECLARATION_AST",
              "unchanged_selection_requires_dependency_review": true
            },
            {
              "current": {
                "declaration_ast_sha256": "ccdd756543d3f31ba49e8cd831e0c8bdde5e1c5a6244281b998bd0a81f5daf73",
                "evidence": {
                  "declaration_kind": "function",
                  "decorated": false,
                  "first_line": 60,
                  "last_line": 62,
                  "limitations": [
                    "Complete physical lines include decorators; no decorator, annotation, import, receiver or call binding is evaluated.",
                    "Lexical class membership is not proof of a runtime interface or inheritance contract."
                  ],
                  "quote": "def typedmethodkey(self, *args, **kwargs):\n    \"\"\"Return a typed cache key for use with cached methods.\"\"\"\n    return typedkey(*args, **kwargs)\n",
                  "quote_byte_end": 1777,
                  "quote_byte_start": 1633,
                  "quote_sha256": "b7f87c1182006cbf34ea8a94285e1ded99213ad2a0d102b616d65f60e89d2f14",
                  "runtime_bindings_verified": false,
                  "selector": "typedmethodkey",
                  "source_executed": false,
                  "syntax_only": true
                },
                "selector": "typedmethodkey",
                "status": "DECLARATION_ESTABLISHED"
              },
              "enclosing_module_changed": true,
              "previous": {
                "reason": "missing or ambiguous callable",
                "selector": "typedmethodkey",
                "status": "DECLARATION_NOT_ESTABLISHED"
              },
              "selector": "typedmethodkey",
              "signal": "DECLARATION_COMPARISON_UNESTABLISHED",
              "unchanged_selection_requires_dependency_review": false
            }
          ],
          "previous_module_ast_sha256": "0bf304e81ad9b0e1c1cfa9b5973f6c0c2d7358211d06d2ed70eb6ad665a0353a",
          "quote_bytes": 868
        },
        "evidence_key": "8b7449079fe167ef7aadbf01d666ffc431464685a0ea7c2131d22cac07535de0",
        "limitations": [
          "Written AST equality is not runtime behavior, dependency completeness or permission to skip a document review.",
          "Source cards are operator-supplied snapshots, not proof of current filesystem state or authenticated repository origin.",
          "Missing or ambiguous selection is never retirement evidence. No documentation action is chosen."
        ]
      }
    }
  ],
  "model_calls": 0,
  "document_writes": 0,
  "source_executed": false,
  "owner_approved": false,
  "training_gold": false,
  "certified_holdout": false,
  "partition": "PREVIOUSLY_EXPOSED_REAL_SOURCE_FAMILY_DEVELOPMENT_REGRESSION",
  "original_v0_1_0_source_preserved": ".local-backups/documentation-intelligence-20261119/revision-signals-v1/before-type-comments-documentation_revision_signals.py"
}
````
<!-- artifact-body:e1ec4a6b8242574bfcb0b2e1a48965fa1534fefc85b80e39fbe00a862dad590f:end -->

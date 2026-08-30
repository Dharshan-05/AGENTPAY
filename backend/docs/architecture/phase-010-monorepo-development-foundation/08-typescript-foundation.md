# AGENTPAY — 08: TypeScript Base Configuration (`tsconfig.base.json`) Specs

## 1. Compiler Flags

* `strict: true`
* `noImplicitAny: true`
* `strictNullChecks: true`
* `noUncheckedIndexedAccess: true`
* `exactOptionalPropertyTypes: true`
* `target: "ES2022"`
* `moduleResolution: "NodeNext"`

All applications inherit from `tsconfig.base.json` via Project References.

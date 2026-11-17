import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

export default [
  ...nextCoreWebVitals,
  {
    ignores: [".next/**", "out/**"],
  },
  {
    rules: {
      // Our data hooks intentionally fetch on mount via refresh() in a useEffect;
      // this rule's new in eslint-plugin-react-hooks 7 and flags that pattern.
      "react-hooks/set-state-in-effect": "warn",
      // Date.now() calls during render for display-only derived values (expiry
      // checks, elapsed-time labels); these new React Compiler purity rules
      // flag that but it's not a correctness bug here.
      "react-hooks/purity": "warn",
    },
  },
];

// Neither `jest-expo` nor `react-native`'s own jest-preset set this for
// React 19 yet - without it, `@testing-library/react-native`'s
// `act(...)`/`renderHook` warn that the environment isn't configured
// for `act`, and `result.current` never populates.
globalThis.IS_REACT_ACT_ENVIRONMENT = true;

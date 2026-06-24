# Task Context

Build a local-first prototype of AI Brief Decoder Lite.

Core flow:

1. User submits a raw brief in the Chrome Extension.
2. Backend decodes it through a provider abstraction.
3. Structured output is validated with Pydantic.
4. The result is stored and rendered back in the extension.

The prototype must run locally without a paid API key by using a fake provider.

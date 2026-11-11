# Built-in image generation: remaining loading screens

The user requested direct generation with the built-in image tool using the unchanged source images. No masking or resubmission to Gemini occurred.

- AA-loading_m4l1: a 16:9 draft was generated. Compositing the unchanged original center revealed duplicate/offset details at the right boundary. One quality retry moved the book and did not satisfy the invariant. Neither output is approved for installation. Both are preserved locally under artifacts-local/imagegen-loading/.
- AA-loading_m4l2: built-in generation rejected at output moderation (request 0305ddb8-6a9c-4caa-8bb1-693f4572f509). Not retried.
- AA-loading_m5l2: built-in generation rejected at output moderation (request 4ece5cd7-400c-465a-95c2-9b35ed9ab37e). Not retried.

The runtime remains at 42 approved backgrounds. Original data, user profiles and deployed packages were not modified. The generated draft is a preview, not an installed correction. No API/CLI fallback was used.

Prompt specification: extend only white side strips of the 16:9 guide, retain the central 4:3 image, match the original tabletop/maps/books/photo edges and soft game texture; historical WWII document props are contextual, no new text, people or symbols. The quality retry specified exact 192-pixel side strips and prohibited duplicate symbols/lettering.

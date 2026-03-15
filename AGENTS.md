# Repository Instructions

## Verification workflow

- Run `make format` often while editing so formatting and fixable lint issues stay small.
- After a few meaningful changes, run `make test`.
- Before handing work back, always run `make itest`.

## Notes

- `make test` already includes `make check`, so type and lint failures should be caught there.
- `make itest` uses the docker-based acceptance stack, so keep acceptance fixtures deterministic and self-contained.

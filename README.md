Requires: uv

```shell
# For running
uv run src/sofun/sofun.py <input>
# uv run src/sofun/sofun.py test_data/libmath_utils.so
# uv run src/sofun/sofun.py test_data/libstring_utils.so

# For testing
cd test_data
make
cd ..
uv run pytest -v
```

# CHANGELOG


## v0.2.0 (2025-06-14)

### Chores

- Adjsut workflow indentation
  ([`2fedf91`](https://github.com/russoz/asciinwriter/commit/2fedf9168a121f38c612dd777e4c98c454cb646f))

### Features

- Force minor release
  ([`0b63177`](https://github.com/russoz/asciinwriter/commit/0b6317788ad1e01dab45aaf99e21d5e68ad1e927))

### Refactoring

- Adjust the release workflow
  ([`5959446`](https://github.com/russoz/asciinwriter/commit/5959446a24c3143fc435f332c8588bb07cb8516d))

- Fix placement of codecov action in release workflow
  ([`4b6776e`](https://github.com/russoz/asciinwriter/commit/4b6776e15e944eeccd25511ea54ff4322bbae188))

- Rename project to asciinwriter
  ([`e19cbb2`](https://github.com/russoz/asciinwriter/commit/e19cbb24bb0afc326774b1fbd22bbe163313bed4))


## v0.1.0 (2025-06-13)

### Chores

- Add devcontainer config
  ([`1c51153`](https://github.com/russoz/asciinwriter/commit/1c511533bd8c2187f1f5a750f917a65fdb396fd6))

- **license**: Update license refs to GPL3+
  ([`d1d17f8`](https://github.com/russoz/asciinwriter/commit/d1d17f82b06f332ffefa949a9109cb7680ca70e5))

- **pre-commit**: Add pre-commit configuration
  ([`c3a3a35`](https://github.com/russoz/asciinwriter/commit/c3a3a350a79f45bf664cde7fbe9fe9c1c24a3049))

- **pre-commit**: Update config
  ([`daee37d`](https://github.com/russoz/asciinwriter/commit/daee37da9aa074adf846f137edecbf725259d538))

- **semantic-release**: Add allow_zero_version=true to settings
  ([`9316ab8`](https://github.com/russoz/asciinwriter/commit/9316ab8fc99f77de949bef40191bda8186851204))

- **semantic-release**: Add contents permission to "build" job
  ([`36f908b`](https://github.com/russoz/asciinwriter/commit/36f908b6fc295e278997c493119f95147290a863))

### Continuous Integration

- Comment out `persist-credentials=false` from checkout action
  ([`0a641a4`](https://github.com/russoz/asciinwriter/commit/0a641a4fdd02ab186f0c65e358b0c79bca355a32))

- Fix settings for release
  ([`980d517`](https://github.com/russoz/asciinwriter/commit/980d517ca0391274144466142049addd4448f527))

- Pass GH_TOKEN as env var to the command
  ([`ff601d0`](https://github.com/russoz/asciinwriter/commit/ff601d072ca3013fb43e590f298ea3799e7f54ee))

- Pass GH_TOKEN as env var to the command
  ([`8fd9364`](https://github.com/russoz/asciinwriter/commit/8fd93649e1b2db4710b98a8efb49e7f4df9d00ca))

- Set project for trusted publishing to PyPI
  ([`f0420fc`](https://github.com/russoz/asciinwriter/commit/f0420fc3aa6182ee79aa093b38047ccf53b0a436))

- Uncomment --cov param for pytest
  ([`577dc68`](https://github.com/russoz/asciinwriter/commit/577dc683831022c73dda86174091db1a58464a05))

### Features

- Accept CLI option to specify file
  ([`0ea464d`](https://github.com/russoz/asciinwriter/commit/0ea464d703b16dc542815be24cbca07df5f64cc2))

- Add new commands ENTER and DELAY
  ([`423d2c2`](https://github.com/russoz/asciinwriter/commit/423d2c255ef798b8962810fcc448df766bd961a5))

- Define files as .scene and adjust code accordingly
  ([`70c41a3`](https://github.com/russoz/asciinwriter/commit/70c41a3071bcf9550190c70d49590e4492fc5d11))

### Refactoring

- Split code into smaller pieces
  ([`06eaa34`](https://github.com/russoz/asciinwriter/commit/06eaa34d5c734694ce281096dec5a772e20637b4))

### Testing

- Add fixture to prevent asciinema output in the test terminal when verbosity < 2
  ([`002d031`](https://github.com/russoz/asciinwriter/commit/002d031d0c29387aa9439b9b0c4d53c51ebeb0f7))

- Add initial tests
  ([`90dd0ee`](https://github.com/russoz/asciinwriter/commit/90dd0eea72717b60019e40bca21b4eae29efbae3))

- Add test with asciinema itself
  ([`6676ca9`](https://github.com/russoz/asciinwriter/commit/6676ca9a52805becbb93cfb16df01116937eccc0))

- Disable workflow for slow tests, remove pytest-skip-slow from project
  ([`d6ce23c`](https://github.com/russoz/asciinwriter/commit/d6ce23c0d8a9c2f3868447243a51166cfd17e84c))


## v0.0.1 (2025-06-07)

- Initial Release

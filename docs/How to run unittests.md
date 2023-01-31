# Unit Testing using unittest

## Steps to run test:

- Navigate to parent directory before running any test:
    ```
    cd src/
    ```

- Run test
    - Run all test in tests (src/tests) module:
        ```
        python3 -m unittest
        ```

    - Run all test in file: 
        ```
        # python3 -m unittest {test_module}.{test_filename}
        # python3 -m unittest {test_module}/{test_filename}.py

        # either one works
        python3 -m unittest tests.test_utilities
        python3 -m unittest tests/test_utilities.py
        ```

    - Run all test in test class: 
        ```
        # python3 -m unittest {test_module}.{test_filename}.{TestClass}

        python3 -m unittest tests.test_utilities.TestUtilities
        ```

    - Run method test case in test class:
        ```
        # python3 -m unittest {test_module}.{test_filename}.{TestClass}.{test_method}

        python3 -m unittest tests.test_main.Test_Main.test_index
        ```

    
## Steps to run test coverage:

- Navigate to parent directory before running any test:
    ```
    cd src/
    ```
- To get coverage report and generate html report:
    ```
    coverage run --source=. -m unittest

    # to omit files add to --omit with comma separated values
    coverage run --source=. --omit=filename.py -m unittest

- Copy and paste
    ```
    coverage run --source=. --omit=res/* -m unittest
    coverage report -m -i
    coverage html -i
    ```

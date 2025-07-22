# A-Fib Prediction at Edge Datasets

This repository contains the datasets which will be used for training,testing and validating the models for A-Fib Prediction at Edge.

This Repository contains the following datasets

- **MIMIC PERform AF Dataset** - [Link](https://ppg-beats.readthedocs.io/en/latest/datasets/mimic_perform_af/) 
    - This dataset is used for training and testing models specifically designed for Atrial Fibrillation prediction.

# Instructions to use this repository
##  Selective Dataset Download with Git LFS

This project uses Git Large File Storage (LFS) to manage large datasets.
To reduce unnecessary bandwidth and disk usage, LFS files are not downloaded automatically. You can clone the repo quickly, and later pull only the datasets you need.

```
.
├── Docs
└── MIMIC-PERform-AF-Dataset
    └── AF-Subjects
```

### Setup Instructions

1. Install Git LFS (if not already installed)

    ```bash
    git lfs install
    ```

2. Clone the repository without downloading large LFS files
To skip all large file downloads on initial clone

    ```bash
    GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/EML-Labs/Datasets
    ```

    This creates the local repo, but LFS files will be pointers, not real files.

3. Pull only the dataset(s) you need
To download only the files under relevant dataset directory, use the following command

    ```bash
    git lfs pull --include="your-dataset-directory/*"
    ``` 
4. (Optional) Globally prevent automatic LFS downloads (advanced)
If you want this behavior to apply to all repos you clone

    ```bash
    git config --global filter.lfs.smudge "git-lfs smudge --skip -- %f"
    ```

    To undo

    ```bash
    git config --global --unset filter.lfs.smudge
    ```

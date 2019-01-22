# Alfred Workflow - ZCY Confluence Search
Quick search in ZCY Confluence

## Hot Key

`cf`

## Usage

1. Save your authentication in `~/.zcy_alfred` like this (you should create this file by yourself)

    ```json
    {
        "username": "your region username",
        "password": "your region password"
    }
    ```

2. Type keywords to search.

    ![Screen Shot](https://raw.githubusercontent.com/Thare-Lam/alfred-zcy-confluence-search/master/screenshot.jpg)

## Download

[ZCY Confluence Search](https://github.com/Thare-Lam/alfred-zcy-confluence-search/releases)

## Upgrade Log

### v1.0.0
- First Release

### v1.0.1
- Add cache to avoid logging in before each use

### v1.0.2
- Remove **requests** package
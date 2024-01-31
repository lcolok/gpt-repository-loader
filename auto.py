import subprocess
import os
import argparse
import yaml


def generate_commands(input_dir, output_dir, project_names):
    return [
        (
            os.path.join(input_dir, project_name),
            os.path.join(output_dir, f"{project_name}.txt"),
        )
        for project_name in project_names
    ]


def ensure_directory_exists(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def update_repo(repo_path):
    os.chdir(repo_path)  # 进入项目目录进行git pull操作
    git_pull_command = ["git", "pull"]
    pull_result = subprocess.run(
        git_pull_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # 返回脚本的当前目录
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    if pull_result.returncode != 0:  # 如果 pull 失败
        # 使用 git stash push 存储未提交的修改
        stash_command = ["git", "stash", "push"]
        stash_result = subprocess.run(
            stash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if stash_result.returncode == 0:
            print("未提交的修改已暂存")
            # 再次尝试 git pull
            subprocess.run(git_pull_command)


def load_repository(repo_path: str, output: str):
    # 执行你的 python 命令
    command = ["python", "gpt_repository_loader.py", repo_path, "-o", output]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.stderr:
        print(f"错误信息: {result.stderr.decode('utf-8')}")
    else:
        print(f"成功存储至: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="更新并加载仓库")
    parser.add_argument("--update_repos", action="store_true", help="是否进行git pull更新仓库")

    args = parser.parse_args()

    # 读取config.yaml
    with open("config.yaml", "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    # 确保输出目录存在
    ensure_directory_exists(config["output_dir"])

    commands = generate_commands(
        config["input_dir"], config["output_dir"], config["project_names"]
    )

    for repo_path, output in commands:
        if args.update_repos:
            update_repo(repo_path)
        load_repository(repo_path, output)

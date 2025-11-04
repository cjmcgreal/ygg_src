import os
import yaml
import pandas as pd
from pathlib import Path

class DataIO:
    def __init__(self, obsidian_path: str):
        """
        Initializes the DataIO class for a given Obsidian vault path.
        
        Args:
            obsidian_path (str): Path to the folder containing markdown notes.
        """
        self.obsidian_path = Path(obsidian_path)

    def read_obsidian_folder_to_df(self, folder_path: str) -> pd.DataFrame:
        """
        Recursively reads all markdown files in an Obsidian folder into a DataFrame.

        Includes:
        - file_name
        - file_path
        - body (entire note excluding frontmatter)
        - All frontmatter keys if frontmatter exists

        Args:
            folder_path (str): Root path of the Obsidian vault or folder.

        Returns:
            pd.DataFrame: DataFrame containing file metadata, body text, and any frontmatter.
        """
        rows = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                if not file.endswith(".md"):
                    continue

                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    row_data = {
                        "file_name": file,
                        "file_path": full_path,
                        "body": ""
                    }

                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) == 3:
                            try:
                                frontmatter = yaml.safe_load(parts[1])
                                if isinstance(frontmatter, dict):
                                    row_data.update(frontmatter)
                                else:
                                    print(f"⚠️ Non-dict frontmatter in {file}")
                            except Exception as e:
                                print(f"⚠️ YAML error in {file}: {e}")
                            row_data["body"] = parts[2].strip()
                        else:
                            print(f"⚠️ Malformed frontmatter in {file}")
                            row_data["body"] = content.strip()
                    else:
                        # No frontmatter, keep full content as body
                        row_data["body"] = content.strip()

                    rows.append(row_data)

                except Exception as e:
                    print(f"⚠️ Error reading file {file}: {e}")

        return pd.DataFrame(rows)

    def write_df_to_obsidian(
            self,
            df: pd.DataFrame,
            export_folder: str,
            filename_col: str = "file_name"
        ) -> None:
            """
            Writes DataFrame rows to markdown files with YAML frontmatter (if any), and body text.
    
            Args:
                df (pd.DataFrame): DataFrame to export.
                export_folder (str): Path to output folder for markdown files.
                filename_col (str): Column in df to use as filename (default 'file_name').
            """
            export_path = Path(export_folder)
            export_path.mkdir(parents=True, exist_ok=True)
    
            for _, row in df.iterrows():
                note_data = row.to_dict()
                filename = note_data.pop(filename_col, "untitled")
                note_body = note_data.pop("body", "").strip()
    
                # Separate frontmatter from body fields
                if note_data:
                    frontmatter = yaml.dump(note_data, sort_keys=False, allow_unicode=True)
                    md_text = f"---\n{frontmatter}---\n\n{note_body}"
                else:
                    # No frontmatter, just body
                    md_text = note_body
    
                out_path = export_path / f"{filename}"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(md_text)


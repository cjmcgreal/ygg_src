from pathlib import Path
import frontmatter

vault_path = Path("/home/conrad/git/yggdrasill/yggdrasill/app/obsidian_reader/_src/test/example_obsidian_folder_structure")  # <<< CHANGE THIS
property_name = "status"
property_value = "new"
file_ext = ".md"

count_updated = 0

for md_file in vault_path.rglob(f"*{file_ext}"):
    try:
        post = frontmatter.load(md_file)

        # Update or insert the frontmatter key
        if post.metadata.get(property_name) != property_value:
            post.metadata[property_name] = property_value

            # Now safely re-dump the full file (metadata + content)
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))

            count_updated += 1
            print(f"✅ Updated: {md_file.relative_to(vault_path)}")

    except Exception as e:
        print(f"⚠️ Skipped {md_file}: {e}")

print(f"\n🏁 Done. Updated {count_updated} files.")

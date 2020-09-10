#!/bin/bash      
# Use case: remove the trailing space on folders and files that OneDrive won't sync on a Mac.
# On a Windows machine, the OneDrive sync tool does this rename automatically.
# Credit: Mateusz Szlosek - https://apple.stackexchange.com/a/174118/279629

# cd "~/OneDrive - {{REPLACE WITH ORGANISATION NAME}}"
cd ~/Downloads

IFS=$'\n'
for file in $(find -d . -name "* ")
do
  target_name=$(echo "$file" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  if [ "$file" != "$target_name" ]; then
      if [ -e $target_name ]; then
          echo "WARNING: $target_name already exists, file not renamed"
      else
          echo "Move $file to $target_name"
          mv "$file" "$target_name"
      fi
  fi
done
echo 'Folders cleaned up.'

# Todo: find out why this isn't working on files with trailing space
IFS=$'\n'
for file in $(find . -name "* ")
do
  target_name=$(echo "$file" | sed 's/[ \t]*$//') 
 if [ "$file" != "$target_name" ]; then 
 if [ -e "$target_name" ]; then
 echo "WARNING: $target_name already exists, file not renamed" 
 else
 echo "Move $file to $target_name"
            mv "$file" "$target_name"
 fi
 fi
done
echo 'Files cleaned up.'
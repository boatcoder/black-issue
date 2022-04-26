There are 2 versions of tasks.py in this repo on master and branchB.  Even though they are formatted differently,
black is happy with both of them which of course leads to merge issues, something I thought black was going to help cut down on.

Try running these commands.

```
git diff branchB
black tasks.py
#All done! ✨ 🍰 ✨
#1 file left unchanged.
git checkout branchB
#Switched to branch 'branchB'
#Your branch is up to date with 'origin/branchB'.
git diff master
black tasks.py
#All done! ✨ 🍰 ✨
#1 file left unchanged.
```

I use this to clear the caches and get the exact same results.....

rm -rf ~/Library/Caches/black/*

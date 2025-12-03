> RELEASE.txt
git describe --long --tags --dirty >> RELEASE.txt
git remote -v | awk '/ \(fetch\)$$/ {print $$2}' >> RELEASE.txt
date -Isec >> RELEASE.txt

GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

ok:
	echo 'OK'
check-all-commited:
	if [ -n "$(GIT_PORCELAIN_STATUS)" ]; \
	then \
	    echo 'YOU HAVE UNCOMMITED CHANGES'; \
	    git status; \
	    exit 1; \
	fi
register: check-all-commited
	python setup.py register
	python setup.py sdist upload
create-sample-images:
	python sample_images.py
upload-sample-images-to-github-pages: check-all-commited create-sample-images
	git branch -D gh-pages
	git checkout -b gh-pages
	git add -f *.png
	git commit -m "Images"
	git push origin gh-pages
	git checkout master

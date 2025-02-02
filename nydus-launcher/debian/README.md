
# Creating new versions

Once you've got a debian/changelog to base your work on,
create new entries in the changelog by doing the following

(the environment variables are used in setting up the version)
```
DEBEMAIL="<email address>"
DEBFULLNAME="<full name>"
export DEBEMAIL
export DEBFULLNAME
dch -v 1.0.2 --distribution jammy
```

The environment variables are needed to set up the information
about the user who created this new version of the package.
-v specifies the exact new version to add to the changelog.
--distribution is needed because if you don't use it, the distro
will be UNRELEASED and subsequent runs of dch will add to the
existing version stanza rather than making a new one.
All distribution values need to be distros which are available
on your current machine. debuild won't build the package if
your version indicates a distribution your machine doesn't
have access to through apt sources. (I think this is what it
checks; I may be wrong).

For the Nydus Launcher you'll need to specify a Ubuntu distro,
since we're intending the Nydus Launcher to work on Ubuntu.

Then it'll open an editor you can write with to
fill out the exact contents of the version.

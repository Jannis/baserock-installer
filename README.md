# Graphical Baserock Installer

## Motivation

Right now, getting start with Baserock is a complex process. Long
instructions have to be read and digested, various files have to be
downloaded, virtual machines have to be set up and configured and so
on. We should aim at making this simple for a few very simple reasons:

* A complex manual installation process bears a high risk of mistakes.
  Since the host systems Baserock is likely to be installed on are
  very non-uniform, any mistake can be hard to spot or diagnose.
* People are impatient and need to have success moments early in the
  process.

This project aims at developing a graphical installer for Baserock
systems. Ideally, this would work on Linux, OS X as well as on Windows.
However, short-term support for Linux and OS X hosts might be
sufficient.

## Concept

### Prerequisite: Repository for Baserock releases

The installer should be able to obtain information about available
releases from different sources on the internet. We can easily make
this happen by storing release information (name, architecture,
development/base, image, staging fillers, trove configuration) in a
Git repository and include its public URL in the release notes.

Each release could be stored in a YAML file and they could be grouped
by "product". E.g. our public releases repository could be structured
as follows:

    /
    /baserock
        water-bomb-devel-x86_64-generic.yaml
        water-bomb-base-x86_64-generic.yaml
    /other
        excalibur-1.2-x86_64-generic.yaml
        excalibur-1.2-armv7-versatile.yaml

The YAML files could look like this:

    name: Baserock / Water Bomb
    arch: x86_64-generic
    kind: development
    image: http://download.baserock.org/baserock/water-bomb-devel-x86_64.img.gz
    fillers:
      - http://download.baserock.org/baserock/water-bomb-x86_64-filler.tar.gz
      - http://download.baserock.org/baserock/water-bomb-x86_64-fix.tar.gz

### The Basics

The installer should be graphical and act like one of those installation
wizards that people are familiar with (especially those working with
Windows).

The following wizard pages seem reasonable at this point:

1. Welcome
2. Select Release Repository
3. Download Releases (automatic, with progress indicator)
4. Select Release
5. Download Release (automatic, with progress indicator(s))
6. Setup Virtual Machine (parameters like: name, source disk size, VM
   type (e.g. VirtualBox), host port for SSH forwarding)
7. VM Setup (automatic, with steps being ticked off; includes creating
   the source partition, copying the staging fillers into the VM,
   creating the morph configuration etc.)
8. Connect Trove (parameters: Trove hostname, name, email, public SSH
   key, optionally ask to create Trove account)
9. Trove Connection (automatic)
10. Completion

### Caching / VM management

The wizard should cache downloaded repositories and files on the host.
It should be able to cancel and repeat easily. Perhaps it should also
remember previous selections and act more like a "Baserock VM manager"
than a simple installer.

### Different VM types

The installer needs to have an abstraction mechanism for configuring,
booting and communicating to VMs using different solutions, including
VirtualBox, libvirt, plain QEMU and others.

### Different architectures

Open question: What does the installer need to know in order to support
different architectures? Is it possible in to achieve this in general?

## Copyright and License

Copyright (c) 2012 Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>

This software project is licensed under the GNU General Public License
version 2.0. For more information see the COPYING file.

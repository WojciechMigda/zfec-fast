
zfex — efficient, portable erasure coding tool
================================================

Generate redundant blocks of information such that if some of the blocks are
lost then the original data can be recovered from the remaining blocks. This
package includes command-line tools, C API, Python API, and Haskell API.

|build| |test-intel| |test-arm| |haskell-api| |unit-tests| |tools| |pypi|

|intel-benchmark|

Intro and Licence
-----------------

This package implements an "erasure code", or "forward error correction
code".

You may use this package under the GNU General Public License, version 2 or,
at your option, any later version.  You may use this package under the
Transitive Grace Period Public Licence, version 1.0 or, at your option, any
later version.  (You may choose to use this package under the terms of either
licence, at your option.)  See the file COPYING.GPL for the terms of the GNU
General Public License, version 2.  See the file COPYING.TGPPL.rst for the
terms of the Transitive Grace Period Public Licence, version 1.0.

The most widely known example of an erasure code is the RAID-5 algorithm
which makes it so that in the event of the loss of any one hard drive, the
stored data can be completely recovered.  The algorithm in the zfec package
has a similar effect, but instead of recovering from the loss of only a
single element, it can be parameterized to choose in advance the number of
elements whose loss it can tolerate.

This package is a fork of ``zfec`` library, which is largely based on
the old "fec" library by Luigi Rizzo et al.,
which is a mature and optimized implementation of erasure coding.  The ``zfex``
package makes several changes from the original ``zfec`` package, including
new C-based benchmark tool and a new SIMD-friendly API.


Installation
------------

Python
......

``pip install zfex``

To run the self-tests, execute ``tox`` from an unpacked source tree or git checkout.

To install ``zfex`` built with custom compilation flags, execute:

``CFLAGS="-O3" pip install git+https://github.com/WojciechMigda/zfex.git``

If ``zfex`` is already cloned locally, then custom compiler flags can be passed to ``setup.py`` to install ``zfex`` like follows:

``CFLAGS="-O3" python setup.py install``

In similar manner, one can override compiler being used. Simply issue:

``CC=arm-linux-gnueabihf-gcc-7 pip install git+https://github.com/WojciechMigda/zfex.git``

Haskell
.......

Building haskell wrapper relies on ``cabal``. The most basic build command is as follows:

``cabal new-build all``

and it will use default C compiler settings. There are few flags available, which control building process:

* ``speed`` will pass highest level optimization flag to the compiler,
* ``ssse3`` will enable SSSE3 optimizations on Intel platform,
* ``neon`` will enable NEON optimizations on Arm platform.

Example build command which uses these flags is below:

``cabal new-build all --flags "speed ssse3"``

For more details, including installing dependencies and running tests, please inspect haskell github actions workflow file.

Community
---------

The source is currently available via git on the web with the command:

``git clone https://github.com/WojciechMigda/zfex``

If you find a bug in ``zfex``, please open an issue on github:

<https://github.com/WojciechMigda/zfex/issues>

Overview
--------

This package performs two operations, encoding and decoding.  Encoding takes
some input data and expands its size by producing extra "check blocks", also
called "secondary blocks".  Decoding takes some data -- any combination of
blocks of the original data (called "primary blocks") and "secondary blocks",
and produces the original data.

The encoding is parameterized by two integers, *k* and *m*.  *m* is the total
number of blocks produced, and *k* is how many of those blocks are necessary to
reconstruct the original data.  *m* is required to be at least 1 and at most
256, and *k* is required to be at least 1 and at most *m*.

(Note that when *k* == *m* then there is no point in doing erasure coding -- it
degenerates to the equivalent of the Unix "split" utility which simply splits
the input into successive segments.  Similarly, when *k* == 1 it degenerates to
the equivalent of the unix "cp" utility -- each block is a complete copy of
the input data.)

Note that each "primary block" is a segment of the original data, so its size
is 1/*k*'th of the size of original data, and each "secondary block" is of the
same size, so the total space used by all the blocks is *m*/*k* times the size of
the original data (plus some padding to fill out the last primary block to be
the same size as all the others).  In addition to the data contained in the
blocks themselves there are also a few pieces of metadata which are necessary
for later reconstruction.  Those pieces are: 1.  the value of *K*, 2.  the
value of *M*, 3.  the sharenum of each block, 4.  the number of bytes of
padding that were used.  The "zfex" command-line tool compresses these pieces
of data and prepends them to the beginning of each share, so each the
sharefile produced by the "zfex" command-line tool is between one and four
bytes larger than the share data alone.

The decoding step requires as input *k* of the blocks which were produced by
the encoding step.  The decoding step produces as output the data that was
earlier input to the encoding step.


Command-Line Tool
-----------------

The bin/ directory contains two Unix-style, command-line tools ``zfex`` and
``zunfex``.  Execute ``zfex --help`` or ``zunfex --help`` for usage
instructions.


Performance
-----------

**TODO: update with new results**

To run the benchmarks, execute the included bench/bench_zfec.py script with
optional --k= and --m= arguments.

On my Athlon 64 2.4 GHz workstation (running Linux), the "zfec" command-line
tool encoded a 160 MB file with m=100, k=94 (about 6% redundancy) in 3.9
seconds, where the "par2" tool encoded the file with about 6% redundancy in
27 seconds.  zfec encoded the same file with m=12, k=6 (100% redundancy) in
4.1 seconds, where par2 encoded it with about 100% redundancy in 7 minutes
and 56 seconds.

The underlying C library in benchmark mode encoded from a file at about 4.9
million bytes per second and decoded at about 5.8 million bytes per second.

On Peter's fancy Intel Mac laptop (2.16 GHz Core Duo), it encoded from a file
at about 6.2 million bytes per second.

On my even fancier Intel Mac laptop (2.33 GHz Core Duo), it encoded from a
file at about 6.8 million bytes per second.

On my old PowerPC G4 867 MHz Mac laptop, it encoded from a file at about 1.3
million bytes per second.

Here is a paper analyzing the performance of various erasure codes and their
implementations, including zfec:

http://www.usenix.org/events/fast09/tech/full_papers/plank/plank.pdf

Zfec shows good performance on different machines and with different values
of K and M. It also has a nice small memory footprint.


API
---

Each block is associated with "blocknum".  The blocknum of each primary block
is its index (starting from zero), so the 0'th block is the first primary
block, which is the first few bytes of the file, the 1'st block is the next
primary block, which is the next few bytes of the file, and so on.  The last
primary block has blocknum *k*-1.  The blocknum of each secondary block is an
arbitrary integer between *k* and 255 inclusive.  (When using the Python API,
if you don't specify which secondary blocks you want when invoking encode(),
then it will by default provide the blocks with ids from *k* to *m*-1 inclusive.)

- C API

  ``fec_encode()`` takes as input an array of *k* pointers, where each pointer
  points to a memory buffer containing the input data (i.e., the *i*'th buffer
  contains the *i*'th primary block).  There is also a second parameter which
  is an array of the blocknums of the secondary blocks which are to be
  produced.  (Each element in that array is required to be the blocknum of a
  secondary block, i.e. it is required to be >= *k* and < *m*.)

  The output from ``fec_encode()`` is the requested set of secondary blocks which
  are written into output buffers provided by the caller.

  There is another encoding API provided, ``fec_encode_simd()``, which imposes
  additional requirements on memory blocks passed, ones which contain input blocks
  of data and those where output block will be written. These blocks are expected
  to be aligned to ``ZFEX_SIMD_ALIGNMENT``. ``fec_encode_simd()`` checks pointers
  to these blocks and returns status code, which equals ``EXIT_SUCCESS`` when
  the validation passed and encoding completed, or ``EXIT_FAILURE`` when input
  and output requirements were not met.

  Note that this ``fec_encode()`` and ``fec_encode_simd()`` are a "low-level" API
  in that it requires the
  input data to be provided in a set of memory buffers of exactly the right
  sizes.  If you are starting instead with a single buffer containing all of
  the data then please see easyfec.py's "class Encoder" as an example of how
  to split a single large buffer into the appropriate set of input buffers
  for ``fec_encode()``.  If you are starting with a file on disk, then please see
  filefec.py's encode_file_stringy_easyfec() for an example of how to read
  the data from a file and pass it to "class Encoder".  The Python interface
  provides these higher-level operations, as does the Haskell interface.  If
  you implement functions to do these higher-level tasks in other languages,
  please send a patch so that your API can be included in future releases of zfex.

  ``fec_decode()`` takes as input an array of *k* pointers, where each pointer
  points to a buffer containing a block.  There is also a separate input
  parameter which is an array of blocknums, indicating the blocknum of each
  of the blocks which is being passed in.

  The output from ``fec_decode()`` is the set of primary blocks which were
  missing from the input and had to be reconstructed.  These reconstructed
  blocks are written into output buffers provided by the caller.


- Python API

  ``encode()`` and ``decode()`` take as input a sequence of *k* buffers, where a
  "sequence" is any object that implements the Python sequence protocol (such
  as a list or tuple) and a "buffer" is any object that implements the Python
  buffer protocol (such as a string or array).  The contents that are
  required to be present in these buffers are the same as for the C API.

  ``encode()`` also takes a list of desired blocknums.  Unlike the C API, the
  Python API accepts blocknums of primary blocks as well as secondary blocks
  in its list of desired blocknums.  ``encode()`` returns a list of buffer
  objects which contain the blocks requested.  For each requested block which
  is a primary block, the resulting list contains a reference to the
  apppropriate primary block from the input list.  For each requested block
  which is a secondary block, the list contains a newly created string object
  containing that block.

  ``decode()`` also takes a list of integers indicating the blocknums of the
  blocks being passed int.  ``decode()`` returns a list of buffer objects which
  contain all of the primary blocks of the original data (in order).  For
  each primary block which was present in the input list, then the result
  list simply contains a reference to the object that was passed in the input
  list.  For each primary block which was not present in the input, the
  result list contains a newly created string object containing that primary
  block.

  Beware of a "gotcha" that can result from the combination of mutable data
  and the fact that the Python API returns references to inputs when
  possible.

  Returning references to its inputs is efficient since it avoids making an
  unnecessary copy of the data, but if the object which was passed as input
  is mutable and if that object is mutated after the call to zfex returns,
  then the result from zfex -- which is just a reference to that same object
  -- will also be mutated.  This subtlety is the price you pay for avoiding
  data copying.  If you don't want to have to worry about this then you can
  simply use immutable objects (e.g. Python strings) to hold the data that
  you pass to ``zfex``.

  Currently, ``fec_encode_simd()`` C API does not have a python wrapper.

- Haskell API

  The Haskell code is fully Haddocked, to generate the documentation, run
  ``runhaskell Setup.lhs haddock``.


Utilities
---------

The ``filefec.py`` module has a utility function for efficiently reading a file
and encoding it piece by piece.  This module is used by the "zfex" and
"zunfex" command-line tools from the bin/ directory.


Dependencies
------------

A C compiler is required.  To use the Python API or the command-line tools a
Python interpreter is also required.  We have tested it with Python v2.7,
v3.5 and v3.6.  For the Haskell interface, GHC >= 6.8.1 is required.


Acknowledgements
----------------

Thanks to the author of the original fec lib, Luigi Rizzo, and the folks that
contributed to it: Phil Karn, Robert Morelos-Zaragoza, Hari Thirumoorthy, and
Dan Rubenstein.  Thanks to the Mnet hackers who wrote an earlier Python
wrapper, especially Myers Carpenter and Hauke Johannknecht.  Thanks to Brian
Warner and Amber O'Whielacronx for help with the API, documentation,
debugging, compression, and unit tests.  Thanks to Adam Langley for improving
the C API and contributing the Haskell API.  Thanks to the creators of GCC
(starting with Richard M. Stallman) and Valgrind (starting with Julian
Seward) for a pair of excellent tools.  Thanks to employees at Allmydata
-- http://allmydata.com -- Fabrice Grinda, Peter Secor, Rob Kinninmont, Brian
Warner, Zandr Milewski, Justin Boreta, Mark Meras for sponsoring part of this work (original ``zfec``)
and releasing it under a Free Software licence. Thanks to Jack Lloyd, Samuel
Neves, and David-Sarah Hopwood.
Last, but not least, thanks to the authors of original ``zfec`` library, from which
this one forked from.
Thanks to Gabs Ricalde, for contributing ARM SIMD-optimized code to ``zfec``, which then
inspired Intel SIMD-optimizations introduced here.


Related Works
-------------

Note: a Unix-style tool like "zfex" does only one thing -- in this case
erasure coding -- and leaves other tasks to other tools.  Other Unix-style
tools that go well with zfex include `GNU tar`_ for archiving multiple files
and directories into one file, `lzip`_ for compression, and `GNU Privacy
Guard`_ for encryption or `b2sum`_ for integrity.  It is important to do
things in order: first archive, then compress, then either encrypt or
integrity-check, then erasure code.  Note that if GNU Privacy Guard is used
for privacy, then it will also ensure integrity, so the use of b2sum is
unnecessary in that case. Note also that you also need to do integrity
checking (such as with b2sum) on the blocks that result from the erasure
coding in *addition* to doing it on the file contents! (There are two
different subtle failure modes -- see "more than one file can match an
immutable file cap" on the `Hack Tahoe-LAFS!`_ Hall of Fame.)

`fecpp`_ is an alternative to zfex. It implements a bitwise-compatible
algorithm to zfex and is BSD-licensed.

.. _GNU tar: http://directory.fsf.org/project/tar/
.. _lzip: http://www.nongnu.org/lzip/lzip.html
.. _GNU Privacy Guard: http://gnupg.org/
.. _b2sum: https://blake2.net/
.. _Hack Tahoe-LAFS!: https://tahoe-lafs.org/hacktahoelafs/
.. _fecpp: http://www.randombit.net/code/fecpp/


Enjoy!


----

.. |pypi| image:: http://img.shields.io/pypi/v/zfex.svg
   :alt: PyPI release status
   :target: https://pypi.python.org/pypi/zfex

.. |build| image:: https://github.com/WojciechMigda/zfex/actions/workflows/build.yml/badge.svg
   :alt: Package Build
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/build.yml

.. |test-intel| image:: https://github.com/WojciechMigda/zfex/actions/workflows/test.yml/badge.svg
   :alt: Tests on Intel hardware
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/test.yml

.. |test-arm| image:: https://github.com/WojciechMigda/zfex/actions/workflows/test-qemu.yml/badge.svg
   :alt: Tests on ARM qemu-emulated environment
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/test-qemu.yml

.. |haskell-api| image:: https://github.com/WojciechMigda/zfex/actions/workflows/haskell-api.yml/badge.svg
   :alt: Haskell API
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/haskell-api.yml

.. |tools| image:: https://github.com/WojciechMigda/zfex/actions/workflows/tools.yml/badge.svg
   :alt: Tools
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/tools.yml

.. |intel-benchmark| image:: bench/images/bench_intel_k7_m10_1M.png
   :alt: Intel benchmark chart
   :target: bench/Results.rst

.. |unit-tests| image:: https://github.com/WojciechMigda/zfex/actions/workflows/utests.yml/badge.svg
   :alt: Unit tests
   :target: https://github.com/WojciechMigda/zfex/actions/workflows/utests.yml

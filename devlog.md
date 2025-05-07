# Dev Log

## [05/06/2025] (Session 1 start) 9:40 AM 

- I reviewed the project requirements for the B-Tree Index File Manager. The project involves building a command-line Python tool to manage B-Tree index files with strict memory constraints and a specific binary file format. My initial focus will be on setting up the project structure and implementing the 'create' command, which initializes a new index file with the correct header format.

## [5/06/2025] (session 1 end) 1:39 PM

- Implemented and tested the 'create' command for initializing a new index file with the correct header format

- Verified error handling for existing files

- Prepared the project structure for the rest of the commands

## [5/06/2025] (session 2 start) 2:30 PM
- I plan on finishing as much of the project as I can in one sitting. I have a lot of other work this week so I will try finishing this project.

## [5/07/2025] (session 2 end) 9:02 AM
- Implemented the 'insert' command to add key/value pairs to the B-Tree, including error handling for duplicates and invalid input
- Added the 'search' command to efficiently find and display key/value pairs in the index file
- Developed the 'load', 'print', and 'extract' commands for bulk operations and data export/import
- Ensured all commands strictly follow the memory constraint of loading at most 3 nodes at a time
- Verified the project by running all commands and confirming correct file format, error handling, and output
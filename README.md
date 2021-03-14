# StrengthTrainingAssistant
Program that uses the python speech recognition library, google cloud, and sqlite to easily allow users to input amount of weight lifted hands free using only their voice, number of reps and also rpe. 
It is designed to work with strength training programs that have a fixed number of days a week and use an expected rpe for work sets.

## Installation
Use package manager pip to to install the dependencies. If pyaudio is failing to install try using pipwin instead of pip.
```bash
pip install PyAudio
pip install SpeechRecognition
pip install pyttsx3
```

## Usage
First use program_schema_entry to create a sqlite database using a program file located in Modules\Database\Programs. 
Programs are written as a .FILE format where each line corresponds to a training session for a given day. Currently the programs I have tested the program with are paid programs
that cannot be distributed freely. As time goes on free programs will be added. For creating own programs use the following example format:

Bench Press, 4,7, 4,8 4,9; Squat 8,7 8,8 8,9

Semi colon is used to split exercises up. For each number pair, 4,7 for instance, the first number refers to the number of reps and the second to the expected rpe for the set.
No semi colon is used at the end of the line.

The program current allows for two forms of back off sets. Either a percentage reduction from the highest weight of the day, or a percentage of the estimated 1 rep maximum also for the given day.
This is done by coding the rpe differently for each type. For first type back off code the rpe as 1.xx where xx is the percentage reduction e.g. 1.95 use 95% of the weight used for the highest set. 
Second type is 2.xx e.g. 2.78 use 78% of the highest estimated 1 rep max for a day.

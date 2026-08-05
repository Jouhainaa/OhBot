# OhBot Behavior Engine

A behavior engine for OhBot, enabling expressive speech, emotional states, natural idle movements, blinking behavior, and AI-generated stand-up comedy using Google Gemini.

## Overview

The **OhBot Behavior Engine** extends the standard OhBot capabilities with a modular framework for realistic social robot behavior.

More information about OhBot can be found at:
https://ohbot.co.uk/

The system combines:

* Emotion-based robot expressions
* lip synchronization
* Natural blinking and idle movements
* AI-generated comedy routines
* Scripted and interactive stand-up comedy
* Voice/text input for user interaction

The goal is to create a more engaging, believable, and entertaining human-robot interaction experience.

## Features

### Emotion System 🎭

The robot can express multiple emotional states:

* Neutral
* Happy
* Thrilled
* Sad
* Angry
* Surprise
* Side-eye
* Disappointed

### Speech 🗣️

Speech is synchronized with facial movements through a viseme-based lip synchronization system.

* Automatic mouth animation
* head movements during speech
* Emotion-specific facial expressions
* Returning to a neutral expression after speaking


### Natural Idle Behavior 👀

While not speaking, the robot continuously performs subtle movements:

* Random blinking
* Eye movements
* Small head motions
* Neutral idle expressions

### Speech Recognition 🎤

Interactive mode supports voice input using: `SpeechRecognition`

The robot can: 

* Listen for audience topics
* Support multiple recognition attempts
* Accept commands such as `stop`, `finish`, or `goodbye`
* Fall back to keyboard input when speech cannot be recognized

### AI Comedy Generation 😂

* Generate jokes
* Adapt jokes to user topics
* Perform short stand-up routines
* Combine AI-generated jokes with expressive robot behavior

## Requirements

- Python 3.11+
- OhBot SDK
- google-genai
- python-dotenv
- SpeechRecognition

## Setup

### Clone Repository

```bash
git clone git@github.com:Jouhainaa/OhBot.git
```

### Install Dependencies

```bash
pip install ohbot
pip install python-dotenv
pip install google-genai
pip install SpeechRecognition
```

## Gemini Setup

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Get your API key from: https://ai.google.dev

## Running the Project


### Complete Stand-up Show

```bash
python standup_show.py
```

## Team

Project developed as part of the Ubiquitous Computing Lab module at the University of Siegen.

Team Members:

* Hassan Khalid Butt
* Sabina Mahmudova
* Jouhaina Salsabil El Euch


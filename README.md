# DewList

Welcome to DewList!

This is an app that is a Work In Progress. It's main function is a "Do List", a way to track tasks.

Some features currently include:

- A login system with username and password
- Adding a task
- Adding a recurrance
- Adding a due date
- A start button with timestamp
- A Pause button with timestamp and reason for pause
- A Resume button with timestamp
- An End Button with timestamp
- An edit button to edit the task

Future features may include:

- Shared Tasks and collaboration _WIP_
- An edit button to edit the task (Reserved for admins) _WIP_
- A delete button to delete the task (Reserved for admins or managers) _WIP_

- A reminder feature with alarm
- intigration into Google Calendar (optional)
- A notification system used to push updates or request updates on tasks
- Tags or Categories grouping (work, personal, errands, etc.) -\_- Priority Levels (low/high, numeric, color coding, customization)
- integration to iCal, in addition to Google Calendar(optional)
-
- activity logs -\_- Natural-language entry("Smith report due tomorrow at 6pm" -> auto-parses into title + due date/time)
- analytics dashboard (charts showing tasks completed per week, day, month, etc with filters for avg completion time, overdue trends)
  -\*- Mobile-Friendly UI

## Getting started

- Open terminal, change directory to projects/private/dewlist, code .
- Open docker
- In terminal:

docker compose down
docker compose up

- open FastAPI: 0.0.0.0:8000/docs

- new terminal, change directory to frontend

npm run dev

- new terminal

## Backend Log

[Complete]
{In Progress}

- [Authorize] (uid:admin@admin.com) (pw: none)

- [register]
- [login]
- [create_task]
- [get_tasks]
- [update_tasks]
- [delete_tasks]
- [toggle_complete]
- [Start_Task]

## Frontend Log

[Complete]
{In Progress}

**_Admin Dashboard button shows up but pressing it attempts to go to the dashboard but gets redirected to localhost:3000_**
**_With the addition of the admin features, some of the tasks are no longer functioning as desired._**

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support

Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap

If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing

State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment

Show your appreciation to those who have contributed to the project.

## License

For open source projects, say how it is licensed.

## Project status

If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.

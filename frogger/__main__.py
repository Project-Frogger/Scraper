from frogger.controller import Controller

controller = Controller()

print("Currently loaded scripts: ")
print("=" * 15)
for number, script in enumerate(controller._installed_scripts):
    print(f"{number + 1}: {script.name} by {script.author}")
print("=" * 15)

script_index = int(input("\n?\tWhich script we should run: "))
controller.run_script_by_index(script_index - 1)

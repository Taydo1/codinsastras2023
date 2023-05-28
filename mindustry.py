from dataclasses import dataclass
import signal
import time
import socketio
import ctypes
import inspect
import threading
from typing import Callable, TypeVar

T = TypeVar('T', int, float)



###########################################################################
##### ------------------------- DATACLASSES ------------------------- #####
###########################################################################

class Items:
    """The internal name of the items"""
    copper = "copper"
    lead = "lead"
    graphite = "graphite"

class Blocks:
    """The internal name of the blocks"""
    core_fondation = "core-foundation"
    titanium_conveyor = "titanium-conveyor"
    junction = "junction"
    router = "router"
    mechanical_drill = "mechanical-drill"
    graphite_press = "graphite-press"
    duo = "duo"
    scatter = "scatter"
    copper_wall = "copper-wall"
    titanium_wall = "titanium-wall"
    ground_factory = "ground-factory"
    air_factory = "air-factory"

class Units:
    """The internal name of the units"""
    dagger = "dagger"
    crawler = "crawler"
    horizon = "horizon"

requirements: dict[str, dict[str, int]] = {
    Blocks.core_fondation : {},
    Blocks.titanium_conveyor : {Items.copper: 1},
    Blocks.junction : {Items.copper: 1},
    Blocks.router : {Items.copper: 1},
    Blocks.mechanical_drill : {Items.copper: 12},
    Blocks.graphite_press : {Items.copper: 75},
    Blocks.duo : {Items.copper: 35},
    Blocks.scatter : {Items.copper: 85, Items.graphite: 15},
    Blocks.copper_wall : {Items.copper: 5},
    Blocks.titanium_wall : {Items.graphite: 3},
    Blocks.ground_factory : {Items.copper: 50},
    Blocks.air_factory : {Items.copper: 60, Items.graphite: 35},
    Units.dagger : {Items.copper: 10},
    Units.crawler : {Items.graphite: 4, Items.lead: 5},
    Units.horizon : {Items.graphite: 15, Items.lead: 10},
}
"""The build or production costs of blocks and units."""

sizes: dict[str, int] = {
    Blocks.core_fondation : 4,
    Blocks.titanium_conveyor : 1,
    Blocks.junction : 1,
    Blocks.router : 1,
    Blocks.mechanical_drill : 2,
    Blocks.graphite_press : 2,
    Blocks.duo : 1,
    Blocks.scatter : 2,
    Blocks.copper_wall : 1,
    Blocks.titanium_wall : 1,
    Blocks.ground_factory : 3,
    Blocks.air_factory : 3,
}
"""The size of the blocks."""

plans: dict[str, int] = {
    Units.dagger: 0,
    Units.crawler: 1,
    Units.horizon: 0,
}
"""The plan id for unit factories."""

class Rotation:
    """Describes the rotation of a block"""
    right = 0
    up = 1
    left = 2
    down = 3

class Generated:
    """All the elements contituting the map."""
    walls = ["red-stone-wall", "carbon-wall", "regolith-wall", "sand-wall", "stone-wall", "spore-wall"]
    ores = ["ore-copper", "ore-lead"]
    floors = ["salt", "sand-floor", "dense-red-stone", "stone"]
    other = ["char", "air"]

@dataclass
class Tile:
    """A tile on the maps."""

    floor: str; """The floor of the tile."""
    
    overlay: str; """The overlay of the tile, such as ores."""

    block: str; """The block built on the tile."""
    rotation: int; """The rotation of the block."""
    team: int; """The team who owns the block."""

    def set_block(self, block: str, rotation: int, team: int):
        """Set the block built on this tile

        Args:
            block (str): the internal name of the block
            team (int): the team who owns the block
        """
        self.block = block
        self.rotation = rotation
        self.team = team

    def clear_block(self):
        """Remove the block from the tile"""
        self.block = ""
        self.team = -1

@dataclass
class Unit:
    """An in game unit."""
    id: int
    """The unique id of the unit."""
    name: str
    """The name of the unit."""

    team: int
    """The team who owns this unit."""
    health: float
    """The health of the unit."""
    x: float
    """The x coordinates of the unit."""
    y: float
    """The y coordinates of the unit."""



###########################################################################
##### ----------------------- MINDUSTRY CLASS ----------------------- #####
###########################################################################

class Mindustry:
    """
    Can be used to make an AI for the game Mindustry. 
    Communicates with the game with socketIO.
    """

    # FIELDS AND CONTRUCTOR
    world: list[list[Tile]]
    """All the tiles of the maps (y, x)."""
    team: int
    """The team of the AI."""

    team_units: list[Unit]
    """Friendly units."""
    ennemy_units: list[Unit]
    """Ennemy units."""

    team_cores: list[tuple[int, int]]
    """The center's coordinate your team's cores."""
    ennemy_cores: list[tuple[int, int, int]]
    """The center's coordinate the other teams' cores."""

    resources: dict[str,int]
    """The ressources in your core."""

    game_time: float
    """The total in-game time."""

    contructions_in_progress: int
    """The amount of build and destroyed not yet handled."""


    def __init__(self, port=2023):
        """Creates an interface for the AI.

        Args:
            port (int, optional): The port for socketIO. Defaults to 2023.
        """
        self._port = port
        self._sio = socketio.Client()
        self._add_callbacks()  # Register callbacks

        self._exit_flag = False # prevent the program from not exiting
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        signal.signal(signal.SIGINT, self._exit_gracefully)

        self._reset()

    def play(self):
        """Connects to Mindustry and starts the AI."""
        print(f"Connecting to Mindustry client on port {self._port}...")
        self._sio.connect(f'http://localhost:{self._port}', wait=False)
        while not self._exit_flag:
            if self._sio.eio.state != 'connected': self._exit_flag = True
            time.sleep(0.1)
        self._sio.disconnect()


    # ABSRACT METHODS
    def setup(self):
        """Sets up the AI. Called before the game starts, after the world and the cores are loaded."""
        pass

    def run(self):
        """
        Called when the game starts of unpauses.
        The code inside the function will be terminated when the game ends of is paused.
        """
        pass

    def block_built(self, x: int, y: int):
        """Called after a block has been built."""
        pass
    
    def block_destroyed(self, x: int, y: int):
        """Called after a block has been destroyed."""
        pass

    def unit_created(self, unit: int):
        """Called after a unit is created."""
        pass
    
    def unit_destroyed(self, unit: int):
        """Called after a unit is destroyed."""
        pass


    # UTILITY
    def sleep_until_built(self):
        """
        Sleeps until all blocks are contructed.
        Wait for an update if no blocks are been contructed.
        """
        if(self.contructions_in_progress != 0):
            while(self.contructions_in_progress > 0):
                time.sleep(0.005)
        else:
            self.sleep_until_update()
    
    def sleep_until_update(self):
        """Wait until the ressources, the game time and the units are updated."""
        update = self._update
        while(update>= self._update):
            time.sleep(0.005)

    def sleep(self, sec: float):
        """Wait for sec in game seconds."""
        start = self.game_time
        while(self.game_time-start < sec):
            time.sleep(0.005)

    def convert_coords(self, x: T, y: T, size: T = 1) -> tuple[T,T]:
        """Converts local coordinates to mindustry coordinates and vice-versa.
        This conversion is done automaticaly.

        Args:
            x, y (T, t): The old coordinates
            size (T, optional): The size of the block concerned. Leave at 1 for units. Defaults to 1.

        Returns:
            tuple[T,T]: The converted coordinates
        """
        return (x,y) if self.team != 2 else (x,len(self.world)-(y+1)-(size+1)%2)
    
    def convert_rotation(self, rotation: int) -> int:
        """Converts local rotation to mindustry rotation and vice-versa.
        This conversion is done automaticaly.

        Args:
            rotation (int): The old rotation. 

        Returns:
            int: The converted rotation.
        """
        return rotation if self.team != 2 or rotation%2 == 0 else 4-rotation


    # CONSTRUCTION
    def build(self, block: str, x: int, y: int, rotation: int = 0):
        """Builds a singular block.

        Args:
            block (str): The block to build.
            x, y (int, int): The coordinates of the new block.
            rotation (int, optional): The rotation of the block. Defaults to 0.
        """
        
        self._sio.emit("build", (block, *self.convert_coords(x, y, sizes[block]), self.convert_rotation(rotation)))
        self.contructions_in_progress +=1

    def build_line(self, block: str, x1: int, y1: int, x2: int, y2: int, rotation: int = 0):
        """Builds a line of block.

        Args:
            block(str) : The type of the block to build
            x1(int), y1(int) : The coordinates of the start of the line
            x2(int), y2(int) : The coordinates of the end of the line
            rotation (int, optional): The rotation of the block. Defaults to 0.
        """
        self._sio.emit("build_line", (block, *self.convert_coords(x1, y1, sizes[block]), *self.convert_coords(x2, y2, sizes[block]), self.convert_rotation(rotation)))
        self.contructions_in_progress +=1
    
    def destroy(self, x: int, y: int):
        """Destroys a block.

        Args:
            x, y (int, int): The coordinates of the block to destroy.
        """
        self._sio.emit("destroy", self.convert_coords(x, y))
        self.contructions_in_progress +=1
    
    def destroy_area(self, x1: int, y1: int, x2: int, y2: int):
        """Destroys all blocks in an area.

        Args:
            x1, y1 (int, int): The coordinates of the top left corner.
            x2, y2 (int, int): The coordinates of the bottom right corner.
        """
        self._sio.emit("destroy_area", (*self.convert_coords(x1, y1), *self.convert_coords(x2, y2)))
        self.contructions_in_progress +=1


    # MAP
    def configure_building(self, x: int, y: int, plan_id: int):
        """Changes the configuration of a building.

        Args:
            x, y (int, int): The coordinates of the building.
            plan_id (int): The id of the plan to select.
        """
        self._sio.emit("configure_building", (*self.convert_coords(x, y, sizes[self.world[y][x].block]), plan_id))


    # UNITS
    def get_unit(self, id: int) -> Unit|None:
        """Get the unit with the specified id.

        Args:
            id (int): The id of the unit.

        Returns:
            Unit|None: The unit with this id.
        """
        if((i:= self.get_team_unit_index(id)) != -1):
            return self.team_units[i]
        if((i:= self.get_ennemy_unit_index(id)) != -1):
            return self.ennemy_units[i]
        return None
    
    def get_unit_index(self, id: int) -> tuple[bool, int]:
        """Get the index of the units, regardless of the team.

        Args:
            id (int): The id of the unit.

        Returns:
            tuple[bool, int]: Whether or not the unit is friendly and its index.
        """

        if(i:= self.get_team_unit_index(id) != -1): return True, i
        if(i:= self.get_ennemy_unit_index(id) != -1): return False, i
        return False, -1

    def get_team_unit_index(self, id: int) -> int:
        """Get the index of a friendly unit `self.team_units`.

        Args:
            id (int): The id of the friendly unit.

        Returns:
            int: The index of the unit. -1 if not found.
        """
        for i, u in enumerate(self.team_units):
            if u.id == id:
                return i
        return -1
    
    def get_ennemy_unit_index(self, id: int) -> int:
        """Get the index of a ennemy unit `self.ennemy_units`.

        Args:
            id (int): The id of the ennemy unit.

        Returns:
            int: The index of the unit. -1 if not found.
        """
        for i, u in enumerate(self.ennemy_units):
            if u.id == id:
                return i
        return -1

    def target_position(self, units: list[int], x: int, y: int):
        """Commands units to attack a block.

        Args:
            units (list[int]): The units to command
            x, y (int, int): The position of the block.
        """
        self._sio.emit("target_position", (units, *self.convert_coords(x, y)))
    
    def target_unit(self, units: list[int], id:int):
        """Commands units to attack another unit.

        Args:
            units (list[int]): The units to command.
            id (int): The unit to attack.
        """
        self._sio.emit("target_unit", (units, id))


    # PRIVATE METHODS AND FIELDS
    _sio: socketio.Client
    _port: int
    _exit_flag: bool

    _ready: bool

    _delta: float

    _update: int

    def _add_callbacks(self):
        # SOCKETIO
        @self._sio.event
        def connect():
            print('Connection established')

        @self._sio.event
        def disconnect():
            print('Disconnected from server')

        @self._sio.event
        def err(message: str):
            print(f"Connection failled: {message}")
            self._exit_flag = True

        # GAME SETUP
        @self._sio.event
        def setup(world: list[list[tuple[str, str, str, int, int]]], team:int, cores: list[tuple[int,int,int]]):
            print("Resetting...")
            self._reset()
            self.team = team
            print("Loading world...")
            if(self.team == 2): world.reverse()
            for line in world:
                tiles = []
                for tile in line:
                    tiles.append(Tile(tile[0], tile[1], tile[2], self.convert_rotation(tile[3]), tile[4]))
                self.world.append(tiles)


            for team, x, y in cores:
                x, y = self.convert_coords(x,y, sizes[Blocks.core_fondation])
                if(team == self.team): self.team_cores.append((x, y))
                else: self.ennemy_cores.append((team, x, y))
            print("Setting up...")
            self.setup()
            self._ready = True


        # AI
        @self._sio.event
        def start(time: float):
            if(self.thread != None): return
            self.game_time = time
            self._assert_ready()
            self.thread = CancellableThread(target=self.run)
            print(f"Started ai in team {self.team}")
            self.thread.start()

        @self._sio.event
        def stop():
            if(self.thread == None): return
            self.thread.terminate()
            self.thread = None
            print("Stopped ai")


        # BLOCKS
        @self._sio.event
        def block_built(x: int, y: int, block: str, rotation:int, team: int):
            x, y = self.convert_coords(x,y, sizes[block])
            self._set_block(x,y, sizes[block], block, self.convert_rotation(rotation), team)
            self.block_built(x,y)

        @self._sio.event
        def block_destroyed(x: int, y: int):
            xt, yt = self.convert_coords(x,y)
            if(self.world[yt][xt].block == "air"): return
            x, y = self.convert_coords(x,y, sizes[self.world[yt][xt].block])
            self.block_destroyed(x,y)
            self._set_block(x,y, sizes[self.world[y][x].block], "air", 0, 0)

        @self._sio.event
        def core_destroyed(x: int, y: int):
            x, y = self.convert_coords(x,y, sizes[Blocks.core_fondation])
            if((x,y) in self.team_cores): self.team_cores.remove((x,y))
            else:
                for i in range(len(self.ennemy_cores)):
                    if(self.ennemy_cores[i][1] == x and self.ennemy_cores[i][2] == y):
                        self.team_cores.pop(i)
                        return
        
        @self._sio.event
        def contruction_finished():
            self.contructions_in_progress -= 1


        # UPDATE
        @self._sio.event
        def update(delta: float, resources: dict[str, int], units: list[tuple[int, str, int, float, float, float]]):
            self._delta = delta
            self.game_time += delta

            self.resources.clear()
            for res, a in resources.items(): self.resources[res] = a

            up_units: dict[int, tuple[int, str, int, float, float, float]] = {}
            for id, type, team, health, x, y in units: up_units[id] = (id, type, team, health, *self.convert_coords(x, y))

            for i in range(len(self.team_units)-1, -1, -1):
                id = self.team_units[i].id
                if (id in up_units):
                    self.team_units[i] = Unit(*up_units[id])
                    up_units.pop(id)
                else:
                    self.unit_destroyed(id)
                    self.team_units.pop(i)
            for i in range(len(self.ennemy_units)-1, -1, -1):
                id = self.ennemy_units[i].id
                if (id in up_units):
                    self.ennemy_units[i] = Unit(*up_units[id])
                    up_units.pop(id)
                else:
                    self.unit_destroyed(id)

            for id, type, team, health, x, y in up_units.values():
                if(team == self.team): self.team_units.append(Unit(id, type, team, health, x, y))
                else: self.ennemy_units.append(Unit(id, type, team, health, x, y))
                self.unit_created(id)
                
            self._update+=1
        

    def _assert_ready(self):
        while not self._ready: time.sleep(0.01)
        assert self.team != 0
        assert len(self.world) != 0
        assert len(self.team_cores) != 0

    def _reset(self):
        self.world = []
        self.team = 0

        self.team_units = []
        self.ennemy_units = []

        self.team_cores = []
        self.ennemy_cores = []

        self._ready = False

        self.contructions_in_progress = 0
        self._update = 0

        self.resources = {}

        self._delta = 0
        self.game_time = 0

        self.thread = None
    
    def _set_block(self, x:int,y:int, size: int, name:str, rotation: int, team:int):
        x -= (size-1)//2
        y -= (size-1)//2
        for j in range(size):
            for i in range(size):
                self.world[y+j][x+i].set_block(name, rotation, team)

    def _exit_gracefully(self, signum, frame):
        self._exit_flag = True


###########################################################################
##### ---------------------------- OTHER ---------------------------- #####
###########################################################################

# Baised on Killable Threads by Tomer Filiba
def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class CancellableThread(threading.Thread):
    '''A thread class that supports raising an exception in the thread from
       another thread.
    '''

    def raise_exc(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL: this function is executed in the context of the
        caller thread, to raise an exception in the context of the
        thread represented by this instance.
        """
        if not self.is_alive() or self.ident is None:
            raise threading.ThreadError("the thread is not active")

        _async_raise(self.ident, exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        while self.is_alive():
            self.raise_exc(SystemExit)
            time.sleep(0.1)

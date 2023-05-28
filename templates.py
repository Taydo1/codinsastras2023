###########################################################################
##### ------------------------ CODE TEMPLATE ------------------------ #####
###########################################################################

from mindustry import *
from utils import *

defense_build = [Blocks.copper_wall, Blocks.titanium_wall, Blocks.duo, Blocks.scatter]
units_build = [Blocks.ground_factory, Blocks.air_factory]
prod_build = [Blocks.graphite_press, Blocks.mechanical_drill]
conveyor_build = [Blocks.titanium_conveyor, Blocks.junction, Blocks.router]
from math import *

def coord_to_id(x, y):
    return x * 1000 + y


def id_to_coord(i):
    x = int(i / 1000)
    return x, i - x * 1000


class AI(Mindustry):
    units = []
    squad_T1=[]
    squad_T2=[]
    squad_T3=[]
    squad_T4=[]
    squad_A1=[]
    step_BO = 1
    BO2=1
    nb_graphite = 0
    to_build = []
    block_base = []
    block_base_id = []

    ennemy_defense = []
    ennemy_units_build = []
    ennemy_prod = []
    ennemy_conveyor = []
    armyLevel = 0
    graphite = False
    graphite_tag = False
    copper_mine_done = {"G1":False, "G2":False, "G3":False, "G4":False, "G5":False, "D1":False, "D2":False, "D3":False, "D4":False, "D5":False}

    air_raid = False
    dca = False

    ph_max = 0

    def build_line(self, block: str, x1: int, y1: int, x2: int, y2: int, rotation: int = 0):
        tile = self.world[y1][x1]
        if tile.team == self.team:
            print("deja placé", tile.block)
            return
        elif tile.team != 0:
            print("il y a qqchose", tile)

        self._sio.emit("build_line", (
            block, *self.convert_coords(x1, y1, sizes[block]), *self.convert_coords(x2, y2, sizes[block]),
            self.convert_rotation(rotation)))
        self.contructions_in_progress += 1

    def verify_built(self):
        tb = len(self.to_build)
        if self.contructions_in_progress == 0:
            if tb > 0:
                to_build_c = self.to_build
                for i in range(tb):
                    val_id = to_build_c[tb - 1 - i]
                    x, y = id_to_coord(val_id)
                    tile = self.world[y][x]
                    self.to_build.pop()
                    if tile.team == self.team:
                        print("déjà placé", tile.block)
                    elif tile.team == 0:
                        print("vide", x, y)
                    else:
                        print("placé par l'ennemi", x, y, tile.block)

    def build(self, block: str, x: int, y: int, rotation: int = 0, destroyed=False):
        tile = self.world[y][x]
        if tile.team != 0 and not destroyed:
            print("block pas libre", tile)
        if tile.team != 0 and not destroyed:
            print("block pas libre", tile)
            return
        self._sio.emit("build", (block, *self.convert_coords(x, y, sizes[block]), self.convert_rotation(rotation)))
        if not destroyed:
            self.to_build.append(coord_to_id(x, y))
        if not destroyed:
            self.to_build.append(coord_to_id(x, y))
        self.contructions_in_progress += 1

    def build_line(self, block: str, x1: int, y1: int, x2: int, y2: int, rotation: int = 0):
        if sizes[block] == 1 and (x1 == x2 or y1 == y2):
            if x1 == x2:
                for i in range(min(y1, y2), max(y1, y2) + 1):
                    self.to_build.append(coord_to_id(x1, i))
                for i in range(min(y1, y2), max(y1, y2) + 1):
                    self.to_build.append(coord_to_id(x1, i))
            else:
                for i in range(min(x1, x2), max(x1, x2) + 1):
                    self.to_build.append(coord_to_id(i, y1))
                    self.to_build.append(coord_to_id(i, y1))
            self._sio.emit("build_line", (
                block, *self.convert_coords(x1, y1, sizes[block]), *self.convert_coords(x2, y2, sizes[block]),
                self.convert_rotation(rotation)))
            self.contructions_in_progress += 1


    def destroy(self, x: int, y: int):
        self._sio.emit("destroy", self.convert_coords(x, y))
        self.contructions_in_progress += 1
        coord_id = coord_to_id(x, y)
        index = self.block_base_id.index(coord_id)
        self.base_block.pop(index)
        self.base_block_id.pop(index)

    def dagger_def(self, puissance):
        if puissance>0:
            for i in range(24, 28):
                #self.build(Blocks.copper_wall, i, 45)
                self.build(Blocks.copper_wall, i, 44)
            for i in range(37, 41):
                #self.build(Blocks.copper_wall, i, 45)
                self.build(Blocks.copper_wall, i, 46)
            for i in range(72, 76):
                #self.build(Blocks.copper_wall, i, 45)
                self.build(Blocks.copper_wall, i, 44)
            for i in range(59, 63):
                #self.build(Blocks.copper_wall, i, 45)
                self.build(Blocks.copper_wall, i, 46)
        for i in range(puissance//4):
            self.build(Blocks.copper_wall, 26, 43-i)
            self.build(Blocks.copper_wall, 38, 44-i)
            self.build(Blocks.duo, 25, 43-i)
            self.build(Blocks.duo, 39, 44-i)
            self.build(Blocks.copper_wall, 73, 43-i)
            self.build(Blocks.copper_wall, 61, 44-i)
            self.build(Blocks.duo, 74, 43-i)
            self.build(Blocks.duo, 60, 44-i)
        if puissance >= 20:
            for i in range(puissance//4):
                #self.build(Blocks.copper_wall, 27, 43-i)
                #self.build(Blocks.copper_wall, 37, 44-i)
                self.build(Blocks.duo, 24, 43-i)
                self.build(Blocks.duo, 40, 44-i)
                #self.build(Blocks.copper_wall, 72, 43-i)
                #self.build(Blocks.copper_wall, 62, 44-i)
                self.build(Blocks.duo, 75, 43-i)
                self.build(Blocks.duo, 59, 44-i)


    buf2 = True
    buf4 = True
    buf6 = True
    buf8 = True
    def horizon_def(self, puissance):
        if puissance > self.ph_max:
            self.ph_max = puissance
            if self.ph_max > 2 and self.buf2:
                self.buf2 = False
                self.build(Blocks.scatter, 49, 40)
                self.build(Blocks.scatter, 49, 42)
            if self.ph_max > 4 and self.buf4:
                self.buf4 = False
                self.build(Blocks.scatter, 49, 44)
                self.build(Blocks.scatter, 18, 39)
                self.build(Blocks.scatter, 79, 39)
            if self.ph_max > 6 and self.buf6:
                self.buf6 = False
                self.build(Blocks.scatter, 15, 39)
                self.build(Blocks.scatter, 82, 39)
                self.build(Blocks.scatter, 43, 42)
                self.build(Blocks.scatter, 55, 42)
            if self.ph_max > 8 and self.buf8:
                self.buf8 = False
                self.build(Blocks.scatter, 43, 39)
                self.build(Blocks.scatter, 55, 39)
                self.build(Blocks.scatter, 21, 36)
                self.build(Blocks.scatter, 76, 36)



    def set_graphite(self):
        self.build_plomb()
        self.sleep_until_built()
        self.protocole()
        self.build_copper("G1")
        self.sleep_until_built()
        self.protocole()
        self.build_copper("G2")
        self.sleep_until_built()
        self.protocole()
        self.build_graphite()

    def base_dca(self):
        self.build("scatter", 21, 39)
        self.build("scatter", 76, 39)
    def protocole(self):
        compteur_d = 0
        compteur_h = 0
        if len(self.ennemy_units) != 0:
            for ennemy in self.ennemy_units:

                if ennemy.name == "dagger" or ennemy.name == Units.crawler:
                    if ennemy.y < 90 :
                        compteur_d += 1
                if ennemy.name == "horizon":
                    compteur_h += 1
                    if not self.dca:
                        self.air_raid = True
                if self.graphite_tag:
                    self.graphite_tag = False
                    self.graphite = True
                    self.set_graphite()
                if self.air_raid and self.getGraphite()>30:
                    self.air_raid = False
                    self.dca = True
                    self.base_dca()
            self.dagger_def(compteur_d)
            self.horizon_def(compteur_h)

    def setup(self):
        self.copper = 500
        self.lead = 0
        self.graphite = 0

        self.units = []
        self.to_build = []
        self.block_base = []
        self.block_base_id = []

        self.ennemy_defense = []
        self.ennemy_units_build = []
        self.ennemy_prod = []
        self.ennemy_conveyor = []

        self.step_BO = 1

        buf2 = True
        buf4 = True
        buf6 = True
        buf8 = True

    def run(self):
        army = 2
        while True:
            self.update_air_army()
            
            if len(self.ennemy_defense) > 0:
                center_def(self.ennemy_defense, self.world)
            if self.step_BO == -1:
                pass
            elif self.step_BO == 1:
                self.build_copper("D1")
                self.sleep_until_built()
                self.protocole()
                if not self.graphite:
                    self.build_copper("G1")
                    self.sleep_until_built()
                    self.protocole()
                self.step_BO += 1

            elif self.step_BO == 2:
                self.fill_mid()
                self.sleep_until_built()
                self.protocole()
                self.step_BO += 1

            elif self.step_BO == 3:
                if not self.graphite:
                    self.build_copper("G2")
                    self.sleep_until_built()
                    self.protocole()
                self.build_copper("G3")
                self.sleep_until_built()
                self.protocole()
                self.step_BO += 1

            elif self.step_BO == 4:
                if not self.graphite:
                    self.build_plomb()
                    self.sleep_until_built()
                    self.protocole()
                self.step_BO += 1

            elif self.step_BO == 5:
                self.build_copper("G4")
                self.sleep_until_built()
                self.protocole()
                self.build_copper("G5")
                self.sleep_until_built()
                self.protocole()
                self.step_BO += 1

            elif self.step_BO == 6:
                self.build_copper("D2")
                self.sleep_until_built()
                self.protocole()
                self.build_copper("D3")
                self.sleep_until_built()
                self.protocole()
                self.build_copper("D4")
                self.sleep_until_built()
                self.protocole()
                self.build_copper("D5")
                self.step_BO+=1

            elif self.step_BO == 7:
                self.build_graphite()
                self.sleep_until_built()
                self.protocole()
                if not self.graphite:
                    self.graphite = True
                    self.build_graphite()
                    self.sleep_until_built()
                    self.protocole()
                self.step_BO += 1

            elif self.step_BO == 8:
                if self.BO2<6:
                    self.set_army(self.BO2)
                    self.BO2+=1
                else:
                    self.step_BO+=1
                self.protocole()
                for i in range(1, 9):
                    if self.world[9][43 - (i * 3)].block == Blocks.ground_factory and self.world[9][56 + (i * 3)].block == Blocks.ground_factory:
                        sself.active_ground(i)
            elif self.step_BO == 9:
                self.set_air_army()
                if self.world[38][15].block==Blocks.air_factory and self.world[38][85].block==Blocks.air_factory:
                    self.active_air()
                self.protocole()
            self.sleep_until_update()



    def set_army(self, number: int):

        self.build(Blocks.ground_factory, 43 - (number * 3), 9, 1)
        self.build(Blocks.ground_factory, 56 + (number * 3), 9, 1)
        self.sleep_until_built()

    def set_air_army(self):
        self.build(Blocks.air_factory, 15, 38, 1)
        self.build(Blocks.air_factory, 85, 38, 1)
        self.sleep_until_built()

    def update_air_army(self):
        gotox0 = []
        gotoy150 = []
        gotonexus = []
        for unity in self.team_units:
            if unity.name == 'horizon':
                x,y = unity.x,unity.y
                if y<115:
                    if x>10:
                        gotox0.append(unity.id)
                    else:
                        gotoy150.append(unity.id)
                else:
                    gotonexus.append(unity.id)
                print(x,y)
        self.target_position(gotox0,0,30)
        self.target_position(gotoy150,0,150)
        self.target_position(gotonexus,50,125)

    def isnexusfree(self):
        pass



    def active_ground(self, number: int):
        self.configure_building(43 - (number * 3), 9, 0)
        self.configure_building(56 + (number * 3), 9, 0)

    def desactive_ground(self, number: int):
        self.configure_building(43 - (number * 3), 9, -1)
        self.configure_building(56 + (number * 3), 9, -1)

    def active_air(self):
        try:
            self.configure_building(15, 38, 0)
            self.configure_building(85, 38, 0)
        except Exception as e:
            pass


    def desactive_air(self):
        try:
            self.configure_building(30, 22, -1)
            self.configure_building(70, 22, -1)
        except Exception as e:
            pass

    def fight_core(self):
        self.target_position(self.units, 50, 125)


    def unitOfId(self, Id:int):
        for i in self.team_units:
            if (i.id==Id):
                return i
    def squad(self,unit: Unit):
        if unit in self.squad_T1:
            return self.squad_T1
        elif unit in self.squad_T2:
            return self.squad_T2
        elif unit in self.squad_T3:
            return self.squad_T3
        elif unit in self.squad_T4:
            return self.squad_T4
        elif unit in self.squad_A1:
            return self.squad_A1

    def unit_created(self, unit: int):
        Unit = self.unitOfId(unit)
        if (Unit!=None):
            self.units.append(unit)
            if (Unit.name=="horizon"):
                self.squad_A1.append(unit)
            elif (Unit.name=="dagger"):
                self.squad_T1.append(unit)
                self.target_position([unit],50,43)
            if (len(self.squad_T1)>1):
                self.cgtAttaque()
                self.target_position(self.squad_T3, 66, 50)
                self.target_position(self.squad_T2, 34, 50)
                self.target_position(self.squad_T4, 50, 125)

    def cgtAttaque(self):
        print(f"1:{len(self.squad_T1)} 2:{len(self.squad_T2)} 3:{len(self.squad_T3)}")
        if (len(self.squad_T2)+len(self.squad_T3)>=20) or len(self.units)>=50:
            self.squad_T4.extend(self.squad_T2)
            self.squad_T2.clear()
            self.squad_T4.extend(self.squad_T3)
            self.squad_T3.clear()
        K=len(self.squad_T1)
        for i in range(int(K/2)):
            self.squad_T2.append(self.squad_T1[i])
        for i in range(int(K/2),K):
            self.squad_T3.append(self.squad_T1[i])
        self.squad_T1.clear()

    def unit_destroyed(self, unit: int):
        try:
            self.units.remove(unit)
            if (self.squad(unit)!=None):
                self.squad(unit).remove(unit)
        except Exception as err:
            pass

    def block_built(self, x: int, y: int):
        tile = self.world[y][x]
        coord_id = coord_to_id(x, y)
        if tile.team == self.team:
            if coord_id in self.to_build:

                self.block_base.append([tile.block, tile.rotation])
                self.block_base_id.append(coord_id)
                try:
                    self.copper -= requirements[tile.block][Items.copper]
                except:
                    None
                try:
                    self.lead -= requirements[tile.block][Items.lead]
                except:
                    None
                try:
                    self.graphite -= requirements[tile.block][Items.graphite]
                except:
                    None

                self.to_build.remove(coord_id)

                self.block_base.append([tile.block, tile.rotation])
                self.block_base_id.append(coord_id)
            else:
                print("ERROR : block NOT IN self.to_build")
        else:
            block = tile.block
            if not self.graphite and self.world[y][x].block == "graphite-press":
                self.graphite_tag = True
            if block in prod_build:
                self.ennemy_prod.append(coord_id)
            elif block in defense_build:
                self.ennemy_defense.append(coord_id)
            elif block in units_build:
                self.ennemy_units_build.append(coord_id)
            else:
                self.ennemy_conveyor.append(coord_id)

    def block_destroyed(self, x: int, y: int):
        id = coord_to_id(x,y)
        if id in self.block_base_id:
            index = self.block_base_id.index(id)
            self.sleep_until_update()
            if y<=60:
                self.build(self.block_base[index][0], x, y, self.block_base[index][1], True)
        tile = self.world[y][x]
        block = tile.block
        if tile.team != self.team:
            if block in prod_build:
                self.ennemy_prod.remove(id)
            elif block in defense_build:
                self.ennemy_defense.remove(id)
            elif block in units_build:
                self.ennemy_units_build.remove(id)
            elif block in conveyor_build:
                self.ennemy_conveyor.remove(id)

    def build_copper(self, id_mine):
        if self.copper_mine_done[id_mine]: return
        self.copper_mine_done[id_mine] = True
        if id_mine == "G1":
            self.build(Blocks.mechanical_drill, 44, 13)
            self.build_line(Blocks.titanium_conveyor, 46, 13, 47, 13, Rotation.right)
            self.build(Blocks.mechanical_drill, 44, 11)
            self.build(Blocks.titanium_conveyor, 46, 12, Rotation.up)
            self.build_line(Blocks.titanium_conveyor, 41, 15, 47, 15, Rotation.right)
            self.build(Blocks.mechanical_drill, 42, 13)
            self.build(Blocks.titanium_conveyor, 48, 15, Rotation.down)
            self.build_line(Blocks.titanium_conveyor, 41, 12, 41, 14, Rotation.up)
            self.build(Blocks.mechanical_drill, 42, 11)
        elif id_mine == "G2":
            self.build(Blocks.mechanical_drill, 11, 11)
            self.build(Blocks.mechanical_drill, 13, 11)
            self.build(Blocks.mechanical_drill, 11, 13)
            self.build(Blocks.mechanical_drill, 13, 13)
            self.build_line(Blocks.titanium_conveyor, 10, 15, 40, 15, Rotation.right)
            self.build_line(Blocks.titanium_conveyor, 10, 12, 10, 14, Rotation.up)
            self.build_line(Blocks.titanium_conveyor, 15, 12, 15, 14, Rotation.up)
            self.build(Blocks.router, 18, 15)
        elif id_mine == "G3":
            self.build(Blocks.mechanical_drill, 11, 16)
            self.build(Blocks.mechanical_drill, 13, 16)
            self.build(Blocks.mechanical_drill, 11, 18)
            self.build(Blocks.mechanical_drill, 13, 18)
            self.build_line(Blocks.titanium_conveyor, 10, 18, 10, 16, Rotation.down)
            self.build_line(Blocks.titanium_conveyor, 15, 18, 15, 16, Rotation.down)
        elif id_mine == "G4":
            self.build(Blocks.mechanical_drill, 11, 21)
            self.build(Blocks.mechanical_drill, 13, 21)
            self.build(Blocks.mechanical_drill, 11, 23)
            self.build(Blocks.mechanical_drill, 13, 23)
            self.build_line(Blocks.titanium_conveyor, 10, 25, 14, 25, Rotation.right)
            self.build_line(Blocks.titanium_conveyor, 10, 22, 10, 24, Rotation.up)
            self.build_line(Blocks.titanium_conveyor, 15, 25, 15, 18, Rotation.down)
        elif id_mine == "G5":
            self.build(Blocks.mechanical_drill, 11, 26)
            self.build(Blocks.mechanical_drill, 13, 26)
            self.build(Blocks.mechanical_drill, 11, 28)
            self.build(Blocks.mechanical_drill, 13, 28)
            self.build_line(Blocks.titanium_conveyor, 10, 28, 10, 26, Rotation.down)
            self.build_line(Blocks.titanium_conveyor, 15, 28, 15, 26, Rotation.down)
        elif id_mine == "D1":
            self.build(Blocks.mechanical_drill, 54, 13)
            self.build_line(Blocks.titanium_conveyor, 53, 13, 52, 13, Rotation.up)
            self.build(Blocks.mechanical_drill, 54, 11)
            self.build(Blocks.titanium_conveyor, 53, 12, Rotation.up)
            self.build(Blocks.mechanical_drill, 56, 13)
            self.build_line(Blocks.titanium_conveyor, 58, 15, 52, 15, Rotation.left)
            self.build(Blocks.titanium_conveyor, 51, 15, Rotation.down)
            self.build(Blocks.mechanical_drill, 56, 11)
            self.build_line(Blocks.titanium_conveyor, 58, 12, 58, 14, Rotation.up)
        elif id_mine == "D2":
            self.build(Blocks.mechanical_drill, 85, 11)
            self.build(Blocks.mechanical_drill, 87, 11)
            self.build(Blocks.mechanical_drill, 85, 13)
            self.build(Blocks.mechanical_drill, 87, 13)
            self.build_line(Blocks.titanium_conveyor, 89, 15, 59, 15, Rotation.right)
            self.build_line(Blocks.titanium_conveyor, 89, 12, 89, 14, Rotation.up)
            self.build_line(Blocks.titanium_conveyor, 84, 12, 84, 14, Rotation.up)
            self.build(Blocks.router, 82, 15)
        elif id_mine == "D3":
            self.build(Blocks.mechanical_drill, 85, 16)
            self.build(Blocks.mechanical_drill, 87, 16)
            self.build(Blocks.mechanical_drill, 85, 18)
            self.build(Blocks.mechanical_drill, 87, 18)
            self.build_line(Blocks.titanium_conveyor, 89, 18, 89, 16, Rotation.down)
            self.build_line(Blocks.titanium_conveyor, 84, 18, 84, 16, Rotation.down)
        elif id_mine == "D4":
            self.build(Blocks.mechanical_drill, 85, 21)
            self.build(Blocks.mechanical_drill, 87, 21)
            self.build(Blocks.mechanical_drill, 85, 23)
            self.build(Blocks.mechanical_drill, 87, 23)
            self.build_line(Blocks.titanium_conveyor, 89, 25, 85, 25, Rotation.right)
            self.build_line(Blocks.titanium_conveyor, 89, 22, 89, 24, Rotation.up)
            self.build_line(Blocks.titanium_conveyor, 84, 25, 84, 18, Rotation.down)
        elif id_mine == "D5":
            self.build(Blocks.mechanical_drill, 85, 26)
            self.build(Blocks.mechanical_drill, 87, 26)
            self.build(Blocks.mechanical_drill, 85, 28)
            self.build(Blocks.mechanical_drill, 87, 28)
            self.build_line(Blocks.titanium_conveyor, 89, 28, 89, 26, Rotation.down)
            self.build_line(Blocks.titanium_conveyor, 84, 28, 84, 26, Rotation.down)

    def build_plomb(self):
        self.build(Blocks.mechanical_drill, 48, 34)
        self.build(Blocks.mechanical_drill, 48, 36)
        self.build(Blocks.mechanical_drill, 50, 34)
        self.build(Blocks.mechanical_drill, 50, 36)
        self.build_line(Blocks.titanium_conveyor, 47, 36, 47, 34, Rotation.down)
        self.build_line(Blocks.titanium_conveyor, 47, 36, 47, 34, Rotation.down)
        self.build_line(Blocks.titanium_conveyor, 52, 36, 52, 34, Rotation.down)
        self.build_line(Blocks.titanium_conveyor, 47, 33, 48, 33, Rotation.down)
        self.build_line(Blocks.titanium_conveyor, 52, 33, 50, 33, Rotation.down)
        self.build_line(Blocks.titanium_conveyor, 49, 33, 49, 15, Rotation.down)

    def build_tourelles(self, side: int):
        if side == Rotation.left:
            self.build_line(Blocks.copper_wall, 28, 58, 37, 58)
            self.build_line(Blocks.duo, 28, 57, 36, 57)
            self.build_line(Blocks.copper_wall, 28, 59, 37, 59)
            self.build_line(Blocks.duo, 28, 56, 36, 56)
            self.build_line(Blocks.copper_wall, 28, 60, 37, 60)
            self.build_line(Blocks.duo, 28, 55, 36, 55)
        else:
            self.build_line(Blocks.copper_wall, 63, 58, 71, 58)
            self.build_line(Blocks.duo, 63, 57, 71, 57)
            self.build_line(Blocks.copper_wall, 63, 59, 71, 59)
            self.build_line(Blocks.duo, 63, 56, 71, 56)
            self.build_line(Blocks.copper_wall, 63, 60, 71, 60)
            self.build_line(Blocks.duo, 63, 55, 71, 55)

    def build_graphite(self):
        if self.nb_graphite >= 1:return
        if self.nb_graphite == 0:
            self.build(Blocks.graphite_press, 20, 16)
            self.build(Blocks.router, 18, 15, True)
            self.build(Blocks.titanium_conveyor, 18, 16, Rotation.up)
            self.build(Blocks.router, 18, 17)
            self.build(Blocks.titanium_conveyor, 19, 17, Rotation.right)
            self.nb_graphite += 1
        elif self.nb_graphite == 1:
            self.build(Blocks.graphite_press, 79, 16)
            self.build(Blocks.router, 82, 15, True)
            self.build(Blocks.titanium_conveyor, 82, 16, Rotation.up)
            self.build(Blocks.router, 82, 17)
            self.build(Blocks.titanium_conveyor, 81, 17, Rotation.left)
            self.nb_graphite += 1
        elif self.nb_graphite == 2:
            self.build(Blocks.graphite_press, 20, 18)
            self.build(Blocks.titanium_conveyor, 18, 18, Rotation.up)
            self.build(Blocks.router, 18, 19)
            self.build(Blocks.titanium_conveyor, 19, 19, Rotation.right)
            self.build_line(Blocks.titanium_conveyor, 22, 19, 22, 16)
            self.nb_graphite += 1
        elif self.nb_graphite == 3:
            self.build(Blocks.graphite_press, 79, 18)
            self.build(Blocks.titanium_conveyor, 82, 18, Rotation.up)
            self.build(Blocks.router, 82, 19)
            self.build(Blocks.titanium_conveyor, 81, 19, Rotation.left)
            self.build_line(Blocks.titanium_conveyor, 78, 19, 78, 16)
            self.nb_graphite += 1

    def fill_mid(self):
        for x in range(42, 57):
            for y in range(66, 72):
                if y % 2 == 0:
                    if x % 4 == 0:
                        self.build(Blocks.titanium_conveyor, x,y, Rotation.up)
                else:
                    if (x+2) % 4 == 0:
                        self.build(Blocks.titanium_conveyor, x,y, Rotation.up)
        """for i in range(28, 72):
            self.build_line(Blocks.titanium_conveyor, i, 62, i, 78)"""
    def getCopper(self):
        try:
            return self.resources[Items.copper]
        except:
            return 0

    def getLead(self):
        try:
            return self.resources[Items.lead]
        except:
            return 0

    def getGraphite(self):
        try:
            return self.resources[Items.graphite]
        except:
            return 0


if __name__ == "__main__":
    AI().play()

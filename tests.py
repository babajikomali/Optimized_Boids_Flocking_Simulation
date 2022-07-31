



        # for i,pos in enumerate(self.boids_pos):
        #     align_circle = Circle(pos[0],pos[1],BoidsFlock.ALIGN_RADIUS)
        #     cohesion_circle = Circle(pos[0],pos[1],BoidsFlock.COHESION_RADIUS)
        #     separation_circle = Circle(pos[0],pos[1],BoidsFlock.SEPARATION_RADIUS)

        #     align_nearby = np.setdiff1d(np.array(rootQuadTree.query(align_circle)),np.array([i]))
        #     cohesion_nearby = np.setdiff1d(np.array(rootQuadTree.query(cohesion_circle)),np.array([i]))
        #     separation_nearby = np.setdiff1d(np.array(rootQuadTree.query(separation_circle)),np.array([i]))

        #     align_vel = np.copy(self.boids_vel)
        #     if len(align_nearby): align_vel = np.delete(align_vel,align_nearby,0)

        #     cohesion_pos = np.copy(self.boids_pos)
        #     if len(cohesion_nearby): cohesion_pos = np.delete(cohesion_pos,cohesion_nearby,0)

        #     separation_pos = np.copy(self.boids_pos)
        #     if len(separation_nearby): separation_pos = np.delete(separation_pos,separation_nearby,0)
        #     boid_pos = self.boids_pos[i,:]
        #     np.broadcast(boid_pos,separation_pos)
        #     separation_pos = boid_pos-separation_pos
            
        #     align_steering = np.sum(align_vel,axis=0)[:,np.newaxis].T
        #     cohesion_steering = np.sum(cohesion_pos,axis=0)[:,np.newaxis].T
        #     separation_steering = np.sum(separation_pos,axis=0)[:,np.newaxis].T

        #     if len(align_nearby): align_steering/=len(align_nearby)
        #     if len(cohesion_nearby): cohesion_steering/=len(cohesion_nearby)
        #     if len(separation_nearby): separation_steering/=len(separation_nearby)

        #     align_steering -= self.boids_vel[i,:]
        #     align_steering = BoidsFlock.setMagnitude(
        #         align_steering, BoidsFlock.ALIGN_MAX_SPEED)
        #     if(np.linalg.norm(align_steering) > BoidsFlock.ALIGN_MAX_FORCE):
        #         align_steering = BoidsFlock.setMagnitude(
        #             align_steering, BoidsFlock.ALIGN_MAX_FORCE)

        #     cohesion_steering -= self.boids_pos[i,:]
        #     cohesion_steering = BoidsFlock.setMagnitude(
        #         cohesion_steering, BoidsFlock.COHESION_MAX_SPEED)
        #     cohesion_steering -= self.boids_vel[i,:]
        #     if(np.linalg.norm(cohesion_steering) > BoidsFlock.COHESION_MAX_FORCE):
        #         cohesion_steering = BoidsFlock.setMagnitude(
        #             cohesion_steering, BoidsFlock.COHESION_MAX_FORCE)
            
        #     separation_steering = BoidsFlock.setMagnitude(
        #         separation_steering, BoidsFlock.SEPARATION_MAX_SPEED)
        #     separation_steering -= self.boids_vel[i,:]
        #     if(np.linalg.norm(separation_steering) > BoidsFlock.SEPARATION_MAX_FORCE):
        #         separation_steering = BoidsFlock.setMagnitude(
        #             separation_steering, BoidsFlock.SEPARATION_MAX_FORCE)

        #     self.boids_acc[i] = align_steering + cohesion_steering - separation_steering

        # self.__update()


        # align_idx = np.zeros([len(align_indices),len(max(align_indices,key = lambda x: len(x)))])
# for i,j in enumerate(align_indices):align_idx[i][0:len(j)] = j
# cohesion_idx = np.zeros([len(cohesion_indices),len(max(cohesion_indices,key = lambda x: len(x)))])
# for i,j in enumerate(cohesion_indices):cohesion_idx[i][0:len(j)] = j
# separation_idx = np.zeros([len(separation_indices),len(max(separation_indices,key = lambda x: len(x)))])
# for i,j in enumerate(separation_indices):separation_idx[i][0:len(j)] = j

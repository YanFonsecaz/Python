import turtle

bob = turtle.Turtle()
print(bob)
# bob.fd(100)
# bob.lt(90)
# bob.fd(100)
# bob.lt(90)
# bob.fd(100)
# bob.lt(90)
# bob.fd(100)
for i in range(4):
    bob.fd(100)
    bob.lt(90)


turtle.mainloop()


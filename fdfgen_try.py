from fdfgen import forge_fdf
fields = [('2','John Smith'),('10','5551234')]
fdf = forge_fdf("",fields,[],[],[])
fdf_file = open("data.fdf","w")
fdf_file.write(fdf)
fdf_file.close()
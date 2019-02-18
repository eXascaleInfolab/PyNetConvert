#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Description: Networks converter from the mathlab format to the nsl
:Authors: Artem Lutov <luart@ya.ru>
:Organizations: eXascale lab <http://exascale.info/>, Lumais <http://www.lumais.com/>
:Date: 2019-02
"""
from __future__ import print_function, division  # Required for stderr output, must be the first import
import os  # Pathes processing
import argparse
import sys
from scipy.io import loadmat


def matToNsl(mnet, dirnet=None):
	"""Convert unsigned input network in the Mathlab .mat format to .nsl

	mnet: str  - unsigned input network in the mathlab format
	dirnet: boolean  - the input network can be directed (adjacency matrix can be asymmetric)
		and directed output network should be produced (.nsa format instead of .nse)
	"""
	print('Converting {}directed network {}...'.format('' if dirnet else 'un', mnet))
	matnet = loadmat(mnet)
	nc = matnet['network'].tocoo()  # Fetch the network data and convert to the COOrdinate format
	assert nc.col.size == nc.row.size and nc.shape[0] == nc.shape[1], (
		'The adjacency matrix is expected to be square')
	# Omit weight in the unweighted matrix
	if nc.data.size == nc.data.sum():
		nc.data = None

	# Create the destination file backing up the existing one if any
	netname = os.path.splitext(mnet)[0]
	netext = '.nsa' if dirnet else '.nse'
	onet = netname + netext
	if os.path.isfile(onet):
		onetbk = onet + '.bck'
		try:
			os.rename(onet, onetbk)
		except OSError:  # On Windows delete the existing file if required
			os.remove(onetbk)
			os.rename(onet, onetbk)
	# Write destination header
	# # NSL[A,E] format specification:
	# # Comments are marked with '#' symbol and allowed only in the begin of the line
	# # Optional Header as a special comment:
	# # [Nodes: <nodes_num>[,]	<Links>: <links_num>[,] [Weighted: {0, 1}]]
	# # Note: the comma is either always present as a delimiter or always absent
	# # Body, links_num lines (not considering comments that might be present)
	# <src_id> <dst_id> [<weight>]
	# ...
	# # where:
	# #  nodes_num  - the number of nodes (vertices) in the network (graph)
	# #  Links  - are either Edges (for the undirected network) or Arcs (for the directed network)
	# #  links_num  - the number of <links> (edges or arcs) in the network
	# #  weighted = {0, 1}  - whether the network is weighted or not, default: 1
	# #
	# #  src_id  - source node id >= 0
	# #  dst_id  - destination node id >= 0
	# #  weight  - weight in case the network is weighted, non-negative floating point number
	links = 0  # The number of links
	wnodes = 0  # The number of weighted nodes (diagonal values != 0)
	with open(onet, 'w') as fout:
		assert dirnet or nc.col.size % 2 == 0, 'Even number of arcs is expected for the {} format: {}'.format(
			netext, nc.col.size)
		fout.write('# Nodes: {}\t{}: {}\tWeighted: {}\n'.format(nc.shape[0], 'Arcs' if dirnet else 'Edges',
			nc.col.size if dirnet else int(nc.col.size / 2), int(nc.data is not None)))
		# Write the body
		sys.stdout.write('  Weighted nodes: ')
		if nc.data is None:
			for i in range(nc.col.size):
				if dirnet or nc.col[i] <= nc.row[i]:
					fout.write('{} {}\n'.format(nc.col[i], nc.row[i]))
					links += 1
					if nc.col[i] == nc.row[i]:
						wnodes += 1
						# sys.stdout.write(' ' + str(nc.col[i]))
		else:
			for i in range(nc.col.size):
				if dirnet or nc.col[i] <= nc.row[i]:
					fout.write('{} {} {}\n'.format(nc.col[i], nc.row[i], nc.data[i]))
					links += 1
					if nc.col[i] == nc.row[i]:
						wnodes += 1
						# sys.stdout.write(' ' + str(nc.col[i]))
		print(' {{{}}}'.format(wnodes))
		if not dirnet and links != nc.col.size / 2:
			if links - wnodes != (nc.col.size - wnodes) / 2:
				print('  WARNING, {} edges formed of the {} expected ({} / {} without the weighted nodes)'
					.format(links, int(nc.col.size / 2), links - wnodes, int((nc.col.size - wnodes) / 2)))
	# Update the header considering weighted nodes if required
	if not dirnet and wnodes:
		if links - wnodes == (nc.col.size - wnodes) / 2:
			print('  Correcting the header')
			onetupd = onet + '.upd'
			with open(onet, 'r') as finp:
				with open(onetupd, 'w') as fout:
					finp.next()
					fout.write('# Nodes: {}\tEdges: {}\tWeighted: {}\n'.format(nc.shape[0],
						links, int(nc.data is not None)))
					for ln in finp:
						fout.write(ln)
			os.remove(onet)  # Note: it is required in Windows to perform rename gracefully
			os.rename(onetupd, onet)
		else:
			print('  WARNING, the imput network has asymmetric adjacency martix and will be processed as directed')
			matToNsl(mnet, dirnet=True)
	print('  converted to', onet)


def parseArgs(params=None):
	"""Parse input parameters (arguments)

	params  - the list of arguments to be parsed (argstr.split()), sys.argv is used if args is None

	return
		directed  - the input networks can be directed (the adjacency matrix can be asymmetric)
			and directed output networks should be produced (.nsa format instead of .nse)
		nets  - input networks to be converted
	"""
	parser = argparse.ArgumentParser(description='Network converter from mathlab format to .nsl (nse/nsa).')
	parser.add_argument('mnets', metavar='MatNet', type=str, nargs='+', help='unsigned input network in the .mat format')
	parser.add_argument('-d', '--directed', dest='directed', action='store_true'
		, help='form directed output network from possibly directed input network')
	args = parser.parse_args(params)
	return args.directed, args.mnets


if __name__ == '__main__':
	dirnet, mnets = parseArgs()
	for mnet in mnets:
		try:
			matToNsl(mnet, dirnet)
		except OSError as err:
			print('  conversion of {} failed: {}', mnet, err)

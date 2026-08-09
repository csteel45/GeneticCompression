/*
 * Node.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.node;


/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jan 29, 2011 2:19:14 AM
 */
public interface Node {

	public int size();
	
	/**
	 * @param args
	 * @return
	 */
	public <T extends Node> Number evaluate();

}


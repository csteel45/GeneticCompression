/*
 * Operand.java
 *
 * Copyright (c) 2011-2026 Chris Steel (FortMoon Consulting, Inc.)
 * SPDX-License-Identifier: MIT
 * See the LICENSE file in the project root for the full license text.
 */
package com.precognizant.genetics.operand;

import java.math.BigInteger;
import java.util.ArrayList;

import com.precognizant.genetics.node.Node;

/**
 * @author Christopher Steel - FortMoon Consulting, Inc.
 *
 * @since Jan 29, 2011 7:53:25 AM
 */
public interface Operand {
	/**
	 * @param param1
	 * @param param2
	 * @return
	 */
	public Number evaluate(Node param1, Node param2);
	
}

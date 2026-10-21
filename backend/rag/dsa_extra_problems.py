"""More bundled DSA problems, so the offline fallback has real variety for every topic and difficulty.

Statements are short paraphrases of well-known LeetCode problems (title and slug match LeetCode, so the
"View on LeetCode" link works). `extend_fallback` merges these into FALLBACK_PROBLEMS without touching
the original bank.
"""

EXTRA_PROBLEMS: dict[str, dict] = {}


def _p(slug: str, title: str, statement: str) -> None:
    EXTRA_PROBLEMS[slug] = {"slug": slug, "title": title, "statement": statement}


# ---- array / general ----
_p("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock",
   "You are given an array prices where prices[i] is the price of a stock on day i. Choose one day to buy and a later day to sell to maximize profit. Return the maximum profit, or 0 if no profit is possible.\n\nExample: prices = [7, 1, 5, 3, 6, 4] -> 5 (buy at 1, sell at 6).\n\nConstraints: 1 <= prices.length <= 10^5, 0 <= prices[i] <= 10^4.")
_p("move-zeroes", "Move Zeroes",
   "Given an integer array nums, move all 0's to the end while keeping the relative order of the non-zero elements. Do it in place, without making a copy of the array.\n\nExample: [0, 1, 0, 3, 12] -> [1, 3, 12, 0, 0].\n\nConstraints: 1 <= nums.length <= 10^4.")
_p("maximum-subarray", "Maximum Subarray",
   "Given an integer array nums, find the contiguous subarray (at least one element) with the largest sum and return that sum.\n\nExample: [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> 6 (subarray [4, -1, 2, 1]).\n\nConstraints: 1 <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4.")
_p("merge-intervals", "Merge Intervals",
   "Given an array of intervals where intervals[i] = [start_i, end_i], merge all overlapping intervals and return the non-overlapping intervals that cover all the input.\n\nExample: [[1,3],[2,6],[8,10],[15,18]] -> [[1,6],[8,10],[15,18]].\n\nConstraints: 1 <= intervals.length <= 10^4, 0 <= start_i <= end_i <= 10^4.")
_p("sliding-window-maximum", "Sliding Window Maximum",
   "You are given an integer array nums and a window size k that slides from the left to the right of the array, one position at a time. Return an array holding the maximum value in each window.\n\nExample: nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3 -> [3, 3, 5, 5, 6, 7].\n\nConstraints: 1 <= k <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4. Aim for O(n).")
_p("shortest-subarray-with-sum-at-least-k", "Shortest Subarray with Sum at Least K",
   "Given an integer array nums and an integer k, return the length of the shortest non-empty subarray of nums whose sum is at least k. If there is no such subarray, return -1.\n\nExample: nums = [2, -1, 2], k = 3 -> 3.\n\nConstraints: 1 <= nums.length <= 10^5, -10^5 <= nums[i] <= 10^5, 1 <= k <= 10^9.")

# ---- hash table ----
_p("isomorphic-strings", "Isomorphic Strings",
   "Given two strings s and t, determine if they are isomorphic: characters in s can be replaced to get t, where every occurrence of a character maps to the same replacement, no two characters map to the same one, and order is preserved.\n\nExample: s = \"egg\", t = \"add\" -> true. s = \"foo\", t = \"bar\" -> false.\n\nConstraints: 1 <= s.length <= 5 * 10^4, t.length == s.length.")
_p("ransom-note", "Ransom Note",
   "Given two strings ransomNote and magazine, return true if ransomNote can be constructed using the letters of magazine, where each letter of magazine may be used only once.\n\nExample: ransomNote = \"aa\", magazine = \"aab\" -> true. ransomNote = \"aa\", magazine = \"ab\" -> false.\n\nConstraints: 1 <= lengths <= 10^5, lowercase English letters.")
_p("longest-consecutive-sequence", "Longest Consecutive Sequence",
   "Given an unsorted array of integers nums, return the length of the longest sequence of consecutive integers (the numbers can appear in any order in the array). Your algorithm must run in O(n) time.\n\nExample: [100, 4, 200, 1, 3, 2] -> 4 (the sequence 1, 2, 3, 4).\n\nConstraints: 0 <= nums.length <= 10^5, -10^9 <= nums[i] <= 10^9.")
_p("subarray-sum-equals-k", "Subarray Sum Equals K",
   "Given an array of integers nums and an integer k, return the total number of contiguous subarrays whose sum equals k.\n\nExample: nums = [1, 1, 1], k = 2 -> 2.\n\nConstraints: 1 <= nums.length <= 2 * 10^4, -1000 <= nums[i] <= 1000, -10^7 <= k <= 10^7.")
_p("max-points-on-a-line", "Max Points on a Line",
   "Given an array points where points[i] = [xi, yi] is a point on the X-Y plane, return the maximum number of points that lie on the same straight line.\n\nExample: [[1,1],[2,2],[3,3]] -> 3. [[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]] -> 4.\n\nConstraints: 1 <= points.length <= 300, all points are unique.")
_p("lfu-cache", "LFU Cache",
   "Design a Least Frequently Used (LFU) cache with a fixed capacity. get(key) returns the value or -1. put(key, value) inserts or updates a key; when the cache is full it first evicts the least frequently used key (ties are broken by evicting the least recently used among them). Reading or writing a key counts as a use. Both operations should run in O(1) average time.\n\nConstraints: 1 <= capacity <= 10^4, up to 2 * 10^5 calls.")

# ---- two pointers ----
_p("merge-sorted-array", "Merge Sorted Array",
   "You are given two sorted integer arrays: nums1 of length m + n (its last n slots are empty zeros) and nums2 of length n. Merge nums2 into nums1 in place so that nums1 is sorted.\n\nExample: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3 -> [1,2,2,3,5,6].\n\nConstraints: 0 <= m, n <= 200, 1 <= m + n <= 200.")
_p("remove-duplicates-from-sorted-array", "Remove Duplicates from Sorted Array",
   "Given an integer array nums sorted in non-decreasing order, remove the duplicates in place so each unique element appears once, keeping the relative order. Return k, the number of unique elements; the first k slots of nums must hold them.\n\nExample: [0,0,1,1,1,2,2,3,3,4] -> k = 5, nums starts [0,1,2,3,4].\n\nConstraints: 1 <= nums.length <= 3 * 10^4.")
_p("container-with-most-water", "Container With Most Water",
   "You are given an integer array height of length n: n vertical lines where line i runs from (i, 0) to (i, height[i]). Choose two lines that, together with the x-axis, form a container holding the most water, and return that amount.\n\nExample: [1,8,6,2,5,4,8,3,7] -> 49.\n\nConstraints: 2 <= n <= 10^5, 0 <= height[i] <= 10^4.")
_p("two-sum-ii-input-array-is-sorted", "Two Sum II - Input Array Is Sorted",
   "Given a 1-indexed array numbers sorted in non-decreasing order, find two numbers that add up to target and return their indices [index1, index2] with index1 < index2. There is exactly one solution and you may not use the same element twice. Use only constant extra space.\n\nExample: numbers = [2, 7, 11, 15], target = 9 -> [1, 2].\n\nConstraints: 2 <= numbers.length <= 3 * 10^4.")
_p("subarrays-with-k-different-integers", "Subarrays with K Different Integers",
   "Given an integer array nums and an integer k, return the number of good subarrays: contiguous subarrays that contain exactly k different integers.\n\nExample: nums = [1,2,1,2,3], k = 2 -> 7.\n\nConstraints: 1 <= nums.length <= 2 * 10^4, 1 <= nums[i], k <= nums.length.")

# ---- dynamic programming ----
_p("fibonacci-number", "Fibonacci Number",
   "The Fibonacci numbers are defined by F(0) = 0, F(1) = 1 and F(n) = F(n-1) + F(n-2). Given n, return F(n).\n\nExample: n = 4 -> 3 (0, 1, 1, 2, 3).\n\nConstraints: 0 <= n <= 30.")
_p("min-cost-climbing-stairs", "Min Cost Climbing Stairs",
   "You are given an array cost where cost[i] is the cost of the i-th step of a staircase. Once you pay the cost you may climb one or two steps. You can start from step 0 or step 1. Return the minimum cost to reach the top (one past the last step).\n\nExample: cost = [10, 15, 20] -> 15.\n\nConstraints: 2 <= cost.length <= 1000, 0 <= cost[i] <= 999.")
_p("house-robber", "House Robber",
   "You are planning to rob houses along a street. nums[i] is the money in house i. Adjacent houses have linked alarms: robbing two adjacent houses on the same night alerts the police. Return the maximum amount you can rob without alerting the police.\n\nExample: [2, 7, 9, 3, 1] -> 12 (rob houses 0, 2 and 4).\n\nConstraints: 1 <= nums.length <= 100, 0 <= nums[i] <= 400.")
_p("longest-increasing-subsequence", "Longest Increasing Subsequence",
   "Given an integer array nums, return the length of the longest strictly increasing subsequence.\n\nExample: [10, 9, 2, 5, 3, 7, 101, 18] -> 4 (for example [2, 3, 7, 101]).\n\nConstraints: 1 <= nums.length <= 2500, -10^4 <= nums[i] <= 10^4. Can you do it in O(n log n)?")
_p("longest-valid-parentheses", "Longest Valid Parentheses",
   "Given a string containing just the characters '(' and ')', return the length of the longest valid (well-formed) parentheses substring.\n\nExample: \"(()\" -> 2. \")()())\" -> 4.\n\nConstraints: 0 <= s.length <= 3 * 10^4.")
_p("burst-balloons", "Burst Balloons",
   "You are given n balloons with numbers nums[i]. Bursting balloon i earns nums[i-1] * nums[i] * nums[i+1] coins (a missing neighbour counts as 1). Burst all the balloons in the best order and return the maximum coins you can collect.\n\nExample: [3, 1, 5, 8] -> 167.\n\nConstraints: 1 <= n <= 300, 0 <= nums[i] <= 100.")

# ---- binary search ----
_p("first-bad-version", "First Bad Version",
   "You have versions 1..n and an API isBadVersion(version). Once a version is bad, every later version is bad too. Find the first bad version while minimising the number of API calls.\n\nExample: n = 5, first bad = 4 -> 4.\n\nConstraints: 1 <= bad <= n <= 2^31 - 1.")
_p("search-insert-position", "Search Insert Position",
   "Given a sorted array of distinct integers and a target value, return the index of the target if it is found, otherwise the index where it would be inserted to keep the array sorted. Your algorithm must run in O(log n).\n\nExample: nums = [1,3,5,6], target = 5 -> 2. target = 2 -> 1.\n\nConstraints: 1 <= nums.length <= 10^4.")
_p("find-first-and-last-position-of-element-in-sorted-array", "Find First and Last Position of Element in Sorted Array",
   "Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value. Return [-1, -1] if the target is not present. Your algorithm must run in O(log n).\n\nExample: nums = [5,7,7,8,8,10], target = 8 -> [3, 4].\n\nConstraints: 0 <= nums.length <= 10^5.")
_p("koko-eating-bananas", "Koko Eating Bananas",
   "Koko has piles of bananas, piles[i] in pile i, and h hours before the guards return. Each hour she picks one pile and eats k bananas from it (if the pile has fewer than k she eats it all and does nothing else that hour). Return the minimum integer k that lets her eat all the bananas within h hours.\n\nExample: piles = [3, 6, 7, 11], h = 8 -> 4.\n\nConstraints: 1 <= piles.length <= h <= 10^9, 1 <= piles[i] <= 10^9.")
_p("split-array-largest-sum", "Split Array Largest Sum",
   "Given an integer array nums and an integer k, split nums into k non-empty contiguous subarrays so that the largest sum of any subarray is minimized. Return that minimized largest sum.\n\nExample: nums = [7, 2, 5, 10, 8], k = 2 -> 18 (split into [7,2,5] and [10,8]).\n\nConstraints: 1 <= nums.length <= 1000, 0 <= nums[i] <= 10^6, 1 <= k <= min(50, nums.length).")
_p("find-k-th-smallest-pair-distance", "Find K-th Smallest Pair Distance",
   "The distance of a pair of integers a and b is |a - b|. Given an integer array nums and an integer k, return the k-th smallest distance among all pairs nums[i], nums[j] with 0 <= i < j < nums.length.\n\nExample: nums = [1, 3, 1], k = 1 -> 0.\n\nConstraints: 2 <= nums.length <= 10^4, 0 <= nums[i] <= 10^6, 1 <= k <= n * (n - 1) / 2.")

# ---- tree ----
_p("invert-binary-tree", "Invert Binary Tree",
   "Given the root of a binary tree, invert the tree (swap the left and right children of every node) and return its root.\n\nExample: [4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1].\n\nConstraints: 0 <= number of nodes <= 100.")
_p("same-tree", "Same Tree",
   "Given the roots p and q of two binary trees, return true if the trees are structurally identical and their nodes have the same values.\n\nExample: p = [1,2,3], q = [1,2,3] -> true. p = [1,2], q = [1,null,2] -> false.\n\nConstraints: 0 <= number of nodes <= 100.")
_p("validate-binary-search-tree", "Validate Binary Search Tree",
   "Given the root of a binary tree, determine whether it is a valid binary search tree: for every node, all keys in its left subtree are strictly smaller and all keys in its right subtree are strictly greater, and both subtrees are valid BSTs.\n\nExample: [2,1,3] -> true. [5,1,4,null,null,3,6] -> false.\n\nConstraints: 1 <= nodes <= 10^4, -2^31 <= Node.val <= 2^31 - 1.")
_p("lowest-common-ancestor-of-a-binary-tree", "Lowest Common Ancestor of a Binary Tree",
   "Given a binary tree and two nodes p and q in it, find their lowest common ancestor: the lowest node that has both p and q as descendants (a node can be a descendant of itself).\n\nExample: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1 -> 3.\n\nConstraints: 2 <= nodes <= 10^5, all values are unique, p != q and both exist in the tree.")
_p("serialize-and-deserialize-binary-tree", "Serialize and Deserialize Binary Tree",
   "Design an algorithm to serialize a binary tree into a string and deserialize that string back into the original tree. There is no restriction on the format, but deserialize(serialize(root)) must rebuild exactly the same tree.\n\nExample: root = [1,2,3,null,null,4,5] -> the same tree after a round trip.\n\nConstraints: 0 <= nodes <= 10^4, -1000 <= Node.val <= 1000.")
_p("recover-binary-search-tree", "Recover Binary Search Tree",
   "You are given the root of a binary search tree in which exactly two nodes had their values swapped by mistake. Recover the tree without changing its structure.\n\nExample: [1,3,null,null,2] -> [3,1,null,null,2].\n\nConstraints: 2 <= nodes <= 1000. Can you do it with O(1) extra space?")

# ---- graph ----
_p("find-the-town-judge", "Find the Town Judge",
   "In a town of n people labeled 1 to n there may be a secret judge who trusts nobody, and whom everybody else trusts. You are given trust, an array of pairs [a, b] meaning a trusts b. Return the judge's label, or -1 if there is no judge.\n\nExample: n = 3, trust = [[1,3],[2,3]] -> 3.\n\nConstraints: 1 <= n <= 1000, 0 <= trust.length <= 10^4.")
_p("flood-fill", "Flood Fill",
   "You are given an m x n grid image of integers, a starting pixel (sr, sc) and a new color. Flood fill: change the starting pixel and every pixel connected to it 4-directionally that has the same original color to the new color. Return the modified image.\n\nExample: image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1, color = 2 -> [[2,2,2],[2,2,0],[2,0,1]].\n\nConstraints: 1 <= m, n <= 50.")
_p("clone-graph", "Clone Graph",
   "Given a reference to a node in a connected undirected graph, return a deep copy (clone) of the whole graph. Each node has an integer val and a list of its neighbors.\n\nExample: adjacency list [[2,4],[1,3],[2,4],[1,3]] -> an identical but completely separate graph.\n\nConstraints: 0 <= nodes <= 100, values 1..100 are unique, no repeated edges or self-loops.")
_p("course-schedule", "Course Schedule",
   "There are numCourses courses labeled 0 to numCourses - 1 and an array prerequisites where [a, b] means you must take course b before course a. Return true if you can finish all courses (that is, the prerequisites contain no cycle).\n\nExample: numCourses = 2, prerequisites = [[1,0]] -> true. prerequisites = [[1,0],[0,1]] -> false.\n\nConstraints: 1 <= numCourses <= 2000, 0 <= prerequisites.length <= 5000.")
_p("critical-connections-in-a-network", "Critical Connections in a Network",
   "There are n servers numbered 0 to n - 1 joined by undirected connections where connections[i] = [a, b]. A connection is critical if removing it leaves some server unable to reach some other server. Return all critical connections in any order.\n\nExample: n = 4, connections = [[0,1],[1,2],[2,0],[1,3]] -> [[1,3]].\n\nConstraints: 2 <= n <= 10^5, n - 1 <= connections.length <= 10^5, the network is connected.")
_p("reconstruct-itinerary", "Reconstruct Itinerary",
   "You are given a list of airline tickets where tickets[i] = [from, to]. Reconstruct the itinerary in order, starting from \"JFK\" and using every ticket exactly once. If several valid itineraries exist, return the one with the smallest lexical order.\n\nExample: [[\"MUC\",\"LHR\"],[\"JFK\",\"MUC\"],[\"SFO\",\"SJC\"],[\"LHR\",\"SFO\"]] -> [\"JFK\",\"MUC\",\"LHR\",\"SFO\",\"SJC\"].\n\nConstraints: 1 <= tickets.length <= 300.")

# ---- linked list ----
_p("merge-two-sorted-lists", "Merge Two Sorted Lists",
   "Merge two sorted linked lists list1 and list2 into one sorted list by splicing together the nodes of the two lists, and return its head.\n\nExample: [1,2,4] and [1,3,4] -> [1,1,2,3,4,4].\n\nConstraints: 0 <= length of each list <= 50, -100 <= Node.val <= 100.")
_p("linked-list-cycle", "Linked List Cycle",
   "Given the head of a linked list, determine whether the list has a cycle in it (some node can be reached again by following next pointers). Try to use O(1) memory.\n\nExample: [3,2,0,-4] where the tail points back to index 1 -> true.\n\nConstraints: 0 <= number of nodes <= 10^4.")
_p("remove-nth-node-from-end-of-list", "Remove Nth Node From End of List",
   "Given the head of a linked list, remove the n-th node from the end of the list and return its head. Try to do it in one pass.\n\nExample: head = [1,2,3,4,5], n = 2 -> [1,2,3,5].\n\nConstraints: 1 <= size <= 30, 1 <= n <= size.")
_p("reorder-list", "Reorder List",
   "You are given the head of a singly linked list L0 -> L1 -> ... -> Ln. Reorder it in place to L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ... without changing node values.\n\nExample: [1,2,3,4] -> [1,4,2,3]. [1,2,3,4,5] -> [1,5,2,4,3].\n\nConstraints: 1 <= nodes <= 5 * 10^4.")
_p("reverse-nodes-in-k-group", "Reverse Nodes in k-Group",
   "Given the head of a linked list, reverse the nodes k at a time and return the modified list. If the number of nodes left over is less than k, leave them as they are. You may only change the nodes themselves, not their values.\n\nExample: head = [1,2,3,4,5], k = 2 -> [2,1,4,3,5]. k = 3 -> [3,2,1,4,5].\n\nConstraints: 1 <= k <= n <= 5000.")

# ---- stack ----
_p("implement-queue-using-stacks", "Implement Queue using Stacks",
   "Implement a first-in-first-out queue using only two stacks. The queue supports push(x), pop(), peek() and empty().\n\nExample: push(1), push(2), peek() -> 1, pop() -> 1, empty() -> false.\n\nConstraints: 1 <= x <= 9, at most 100 calls, pop and peek are only called on a non-empty queue.")
_p("backspace-string-compare", "Backspace String Compare",
   "Given two strings s and t, return true if they are equal when both are typed into empty text editors, where '#' means a backspace (backspacing an empty text does nothing).\n\nExample: s = \"ab#c\", t = \"ad#c\" -> true (both become \"ac\").\n\nConstraints: 1 <= s.length, t.length <= 200, lowercase letters and '#'.")
_p("evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation",
   "You are given an array of strings tokens representing an arithmetic expression in Reverse Polish Notation. Evaluate it and return the integer result. Valid operators are +, -, * and /; division truncates toward zero.\n\nExample: [\"2\",\"1\",\"+\",\"3\",\"*\"] -> 9.\n\nConstraints: 1 <= tokens.length <= 10^4, the expression is always valid.")
_p("min-stack", "Min Stack",
   "Design a stack that supports push, pop, top and retrieving the minimum element, each in constant time.\n\nExample: push(-2), push(0), push(-3), getMin() -> -3, pop(), top() -> 0, getMin() -> -2.\n\nConstraints: -2^31 <= val <= 2^31 - 1, pop, top and getMin are only called on a non-empty stack.")
_p("basic-calculator", "Basic Calculator",
   "Given a string s representing a valid expression made of non-negative integers, '+', '-', parentheses and spaces, evaluate it and return the result. You may not use eval().\n\nExample: s = \"(1+(4+5+2)-3)+(6+8)\" -> 23.\n\nConstraints: 1 <= s.length <= 3 * 10^5.")
_p("maximal-rectangle", "Maximal Rectangle",
   "Given a rows x cols binary matrix filled with '0' and '1', find the largest rectangle containing only '1's and return its area.\n\nExample: [[\"1\",\"0\",\"1\",\"0\",\"0\"],[\"1\",\"0\",\"1\",\"1\",\"1\"],[\"1\",\"1\",\"1\",\"1\",\"1\"],[\"1\",\"0\",\"0\",\"1\",\"0\"]] -> 6.\n\nConstraints: 1 <= rows, cols <= 200.")

# ---- greedy ----
_p("lemonade-change", "Lemonade Change",
   "At a lemonade stand each lemonade costs $5. Customers pay with a $5, $10 or $20 bill in the order given by bills, and you must give correct change (you start with none). Return true if you can give every customer correct change.\n\nExample: [5,5,5,10,20] -> true. [5,5,10,10,20] -> false.\n\nConstraints: 1 <= bills.length <= 10^5.")
_p("can-place-flowers", "Can Place Flowers",
   "You have a flowerbed represented by an array of 0s (empty) and 1s (planted). Flowers cannot be planted in adjacent plots. Given n, return true if n new flowers can be planted without breaking that rule.\n\nExample: flowerbed = [1,0,0,0,1], n = 1 -> true. n = 2 -> false.\n\nConstraints: 1 <= flowerbed.length <= 2 * 10^4.")
_p("gas-station", "Gas Station",
   "There are n gas stations on a circular route. gas[i] is the fuel at station i and cost[i] is the fuel needed to travel to the next station. Starting with an empty tank at one of the stations, return the index of the starting station from which you can travel around the circuit once clockwise, or -1 if it is impossible. If a solution exists it is unique.\n\nExample: gas = [1,2,3,4,5], cost = [3,4,5,1,2] -> 3.\n\nConstraints: 1 <= n <= 10^5.")
_p("partition-labels", "Partition Labels",
   "Given a string s, partition it into as many parts as possible so that each letter appears in at most one part. Return a list of the sizes of the parts.\n\nExample: s = \"ababcbacadefegdehijhklij\" -> [9, 7, 8].\n\nConstraints: 1 <= s.length <= 500, lowercase English letters.")
_p("ipo", "IPO",
   "A company wants to maximize its capital before an IPO and can finish at most k distinct projects. Project i needs at least capital[i] to start and adds profits[i] to your capital when finished. Starting with w capital, return the maximum capital you can have after at most k projects.\n\nExample: k = 2, w = 0, profits = [1,2,3], capital = [0,1,1] -> 4.\n\nConstraints: 1 <= k <= 10^5, 0 <= w <= 10^9, up to 10^5 projects.")
_p("minimum-number-of-refueling-stops", "Minimum Number of Refueling Stops",
   "A car travels from position 0 to a target at distance target miles, starting with startFuel liters (1 liter = 1 mile). stations[i] = [position_i, fuel_i] are gas stations along the way. Return the minimum number of refueling stops needed to reach the target, or -1 if it is impossible.\n\nExample: target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]] -> 2.\n\nConstraints: 1 <= target, startFuel <= 10^9, 0 <= stations.length <= 500.")

# ---- backtracking ----
_p("binary-tree-paths", "Binary Tree Paths",
   "Given the root of a binary tree, return all root-to-leaf paths in any order, each written as a string like \"a->b->c\".\n\nExample: root = [1,2,3,null,5] -> [\"1->2->5\", \"1->3\"].\n\nConstraints: 1 <= nodes <= 100, -100 <= Node.val <= 100.")
_p("sum-of-all-subset-xor-totals", "Sum of All Subset XOR Totals",
   "The XOR total of an array is the XOR of all its elements (0 for an empty array). Given an array nums, return the sum of the XOR totals of every subset of nums.\n\nExample: nums = [1, 3] -> 6 (subsets [], [1], [3], [1,3] give 0, 1, 3, 2).\n\nConstraints: 1 <= nums.length <= 12, 1 <= nums[i] <= 20.")
_p("permutations", "Permutations",
   "Given an array nums of distinct integers, return all possible permutations in any order.\n\nExample: [1,2,3] -> [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]].\n\nConstraints: 1 <= nums.length <= 6, all integers are unique.")
_p("combination-sum", "Combination Sum",
   "Given an array of distinct integers candidates and a target integer, return all unique combinations of candidates that sum to target. The same number may be used an unlimited number of times.\n\nExample: candidates = [2,3,6,7], target = 7 -> [[2,2,3],[7]].\n\nConstraints: 1 <= candidates.length <= 30, 2 <= candidates[i] <= 40, 1 <= target <= 40.")
_p("generate-parentheses", "Generate Parentheses",
   "Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.\n\nExample: n = 3 -> [\"((()))\",\"(()())\",\"(())()\",\"()(())\",\"()()()\"].\n\nConstraints: 1 <= n <= 8.")
_p("sudoku-solver", "Sudoku Solver",
   "Write a program that solves a Sudoku puzzle by filling the empty cells (marked '.'). Every digit 1-9 must appear exactly once in each row, each column and each of the nine 3x3 sub-boxes. The input board has exactly one solution.\n\nConstraints: board.length == 9, board[i].length == 9, each cell is a digit 1-9 or '.'.")
_p("word-search-ii", "Word Search II",
   "Given an m x n board of characters and a list of words, return all words that can be built from letters of sequentially adjacent cells (horizontally or vertically), using each cell at most once per word.\n\nExample: board = [[\"o\",\"a\",\"a\",\"n\"],[\"e\",\"t\",\"a\",\"e\"],[\"i\",\"h\",\"k\",\"r\"],[\"i\",\"f\",\"l\",\"v\"]], words = [\"oath\",\"pea\",\"eat\",\"rain\"] -> [\"eat\",\"oath\"].\n\nConstraints: 1 <= m, n <= 12, 1 <= words.length <= 3 * 10^4.")

# ---- sorting ----
_p("squares-of-a-sorted-array", "Squares of a Sorted Array",
   "Given an integer array nums sorted in non-decreasing order, return an array of the squares of each number, also sorted in non-decreasing order.\n\nExample: [-4,-1,0,3,10] -> [0,1,9,16,100].\n\nConstraints: 1 <= nums.length <= 10^4, -10^4 <= nums[i] <= 10^4. Can you do it in O(n)?")
_p("relative-sort-array", "Relative Sort Array",
   "Given two arrays arr1 and arr2, where the elements of arr2 are distinct and all appear in arr1, sort arr1 so that its items follow the relative order of arr2. Elements not in arr2 go at the end in ascending order.\n\nExample: arr1 = [2,3,1,3,2,4,6,7,9,2,19], arr2 = [2,1,4,3,9,6] -> [2,2,2,1,4,3,3,9,6,7,19].\n\nConstraints: 1 <= arr1.length, arr2.length <= 1000.")
_p("kth-largest-element-in-an-array", "Kth Largest Element in an Array",
   "Given an integer array nums and an integer k, return the k-th largest element in sorted order (not the k-th distinct element). Can you solve it without fully sorting the array?\n\nExample: [3,2,1,5,6,4], k = 2 -> 5.\n\nConstraints: 1 <= k <= nums.length <= 10^5.")
_p("maximum-gap", "Maximum Gap",
   "Given an integer array nums, return the maximum difference between two successive elements in its sorted form, or 0 if it has fewer than two elements. You must write an algorithm that runs in linear time and uses linear extra space.\n\nExample: [3,6,9,1] -> 3.\n\nConstraints: 1 <= nums.length <= 10^5, 0 <= nums[i] <= 10^9.")
_p("reverse-pairs", "Reverse Pairs",
   "Given an integer array nums, return the number of reverse pairs: pairs (i, j) where 0 <= i < j < nums.length and nums[i] > 2 * nums[j].\n\nExample: [1,3,2,3,1] -> 2.\n\nConstraints: 1 <= nums.length <= 5 * 10^4, -2^31 <= nums[i] <= 2^31 - 1.")

# ---- string ----
_p("longest-common-prefix", "Longest Common Prefix",
   "Write a function to find the longest common prefix string amongst an array of strings. If there is no common prefix, return an empty string.\n\nExample: [\"flower\",\"flow\",\"flight\"] -> \"fl\". [\"dog\",\"racecar\",\"car\"] -> \"\".\n\nConstraints: 1 <= strs.length <= 200, 0 <= strs[i].length <= 200, lowercase letters.")
_p("reverse-string", "Reverse String",
   "Write a function that reverses a string given as an array of characters s. You must do it in place with O(1) extra memory.\n\nExample: [\"h\",\"e\",\"l\",\"l\",\"o\"] -> [\"o\",\"l\",\"l\",\"e\",\"h\"].\n\nConstraints: 1 <= s.length <= 10^5, printable ASCII characters.")
_p("longest-palindromic-substring", "Longest Palindromic Substring",
   "Given a string s, return the longest palindromic substring in s.\n\nExample: s = \"babad\" -> \"bab\" (\"aba\" is also valid). s = \"cbbd\" -> \"bb\".\n\nConstraints: 1 <= s.length <= 1000, s consists of digits and English letters.")
_p("decode-string", "Decode String",
   "Given an encoded string, return its decoded string. The encoding rule is k[encoded_string], meaning encoded_string is repeated exactly k times; encodings can be nested.\n\nExample: s = \"3[a]2[bc]\" -> \"aaabcbc\". s = \"3[a2[c]]\" -> \"accaccacc\".\n\nConstraints: 1 <= s.length <= 30, 1 <= k <= 300, the input is always valid.")
_p("regular-expression-matching", "Regular Expression Matching",
   "Given an input string s and a pattern p, implement regular expression matching with support for '.' (matches any single character) and '*' (matches zero or more of the preceding element). The match must cover the entire string.\n\nExample: s = \"aa\", p = \"a*\" -> true. s = \"ab\", p = \".*\" -> true. s = \"mississippi\", p = \"mis*is*p*.\" -> false.\n\nConstraints: 1 <= s.length, p.length <= 20.")
_p("shortest-palindrome", "Shortest Palindrome",
   "You are given a string s. You can turn it into a palindrome by adding characters only in front of it. Return the shortest palindrome you can make this way.\n\nExample: s = \"aacecaaa\" -> \"aaacecaaa\". s = \"abcd\" -> \"dcbabcd\".\n\nConstraints: 0 <= s.length <= 5 * 10^4.")

# ---- heap ----
_p("kth-largest-element-in-a-stream", "Kth Largest Element in a Stream",
   "Design a class that finds the k-th largest element in a stream of numbers (the k-th largest in sorted order, not the k-th distinct). KthLargest(k, nums) initialises it; add(val) appends val and returns the current k-th largest.\n\nExample: k = 3, nums = [4,5,8,2]; add(3) -> 4; add(5) -> 5; add(10) -> 5.\n\nConstraints: 1 <= k <= 10^4, up to 10^4 calls to add.")
_p("relative-ranks", "Relative Ranks",
   "You are given an integer array score where score[i] is the score of the i-th athlete (all scores are unique). The top three athletes get \"Gold Medal\", \"Silver Medal\" and \"Bronze Medal\"; everyone else gets their placement number as a string. Return the answer array.\n\nExample: [5,4,3,2,1] -> [\"Gold Medal\",\"Silver Medal\",\"Bronze Medal\",\"4\",\"5\"].\n\nConstraints: 1 <= n <= 10^4, 0 <= score[i] <= 10^6.")
_p("task-scheduler", "Task Scheduler",
   "You are given an array of CPU tasks labeled A-Z and a cooling interval n. Each task takes one unit of time, and two identical tasks must be separated by at least n units (idle slots are allowed). Return the minimum number of time units needed to finish all tasks.\n\nExample: tasks = [\"A\",\"A\",\"A\",\"B\",\"B\",\"B\"], n = 2 -> 8.\n\nConstraints: 1 <= tasks.length <= 10^4, 0 <= n <= 100.")

# ---- sliding window ----
_p("contains-duplicate-ii", "Contains Duplicate II",
   "Given an integer array nums and an integer k, return true if there are two distinct indices i and j with nums[i] == nums[j] and |i - j| <= k.\n\nExample: nums = [1,2,3,1], k = 3 -> true. nums = [1,2,3,1,2,3], k = 2 -> false.\n\nConstraints: 1 <= nums.length <= 10^5, 0 <= k <= 10^5.")
_p("minimum-difference-between-highest-and-lowest-of-k-scores", "Minimum Difference Between Highest and Lowest of K Scores",
   "You are given an array nums of scores and an integer k. Pick the scores of any k students so that the difference between the highest and the lowest of the k scores is as small as possible, and return that minimum difference.\n\nExample: nums = [9, 4, 1, 7], k = 2 -> 2.\n\nConstraints: 1 <= k <= nums.length <= 1000, 0 <= nums[i] <= 10^5.")
_p("longest-repeating-character-replacement", "Longest Repeating Character Replacement",
   "You are given a string s of uppercase letters and an integer k. You may change any character to any other uppercase letter at most k times. Return the length of the longest substring containing the same letter you can get after those changes.\n\nExample: s = \"AABABBA\", k = 1 -> 4.\n\nConstraints: 1 <= s.length <= 10^5, 0 <= k <= s.length.")
_p("minimum-size-subarray-sum", "Minimum Size Subarray Sum",
   "Given an array of positive integers nums and a positive integer target, return the minimal length of a contiguous subarray whose sum is at least target, or 0 if no such subarray exists.\n\nExample: target = 7, nums = [2,3,1,2,4,3] -> 2 (the subarray [4,3]).\n\nConstraints: 1 <= target <= 10^9, 1 <= nums.length <= 10^5, 1 <= nums[i] <= 10^4.")
_p("permutation-in-string", "Permutation in String",
   "Given two strings s1 and s2, return true if s2 contains a permutation of s1 (that is, some substring of s2 is an anagram of s1).\n\nExample: s1 = \"ab\", s2 = \"eidbaooo\" -> true. s1 = \"ab\", s2 = \"eidboaoo\" -> false.\n\nConstraints: 1 <= s1.length, s2.length <= 10^4, lowercase English letters.")


# Slugs to add per topic and difficulty. A slug that is not in EXTRA_PROBLEMS must already exist in the original bank.
EXTRA_BY_TOPIC: dict[str, dict[str, list[str]]] = {
    "array": {
        "easy": ["best-time-to-buy-and-sell-stock", "move-zeroes"],
        "medium": ["maximum-subarray", "merge-intervals"],
        "hard": ["sliding-window-maximum", "shortest-subarray-with-sum-at-least-k"],
    },
    "hash-table": {
        "easy": ["isomorphic-strings", "ransom-note"],
        "medium": ["longest-consecutive-sequence", "subarray-sum-equals-k"],
        "hard": ["max-points-on-a-line", "lfu-cache"],
    },
    "two-pointers": {
        "easy": ["merge-sorted-array", "remove-duplicates-from-sorted-array"],
        "medium": ["container-with-most-water", "two-sum-ii-input-array-is-sorted"],
        "hard": ["subarrays-with-k-different-integers", "minimum-window-substring"],
    },
    "dynamic-programming": {
        "easy": ["fibonacci-number", "min-cost-climbing-stairs"],
        "medium": ["house-robber", "longest-increasing-subsequence"],
        "hard": ["longest-valid-parentheses", "burst-balloons"],
    },
    "binary-search": {
        "easy": ["first-bad-version", "search-insert-position"],
        "medium": ["find-first-and-last-position-of-element-in-sorted-array", "koko-eating-bananas"],
        "hard": ["split-array-largest-sum", "find-k-th-smallest-pair-distance"],
    },
    "tree": {
        "easy": ["invert-binary-tree", "same-tree"],
        "medium": ["validate-binary-search-tree", "lowest-common-ancestor-of-a-binary-tree"],
        "hard": ["serialize-and-deserialize-binary-tree", "recover-binary-search-tree"],
    },
    "graph": {
        "easy": ["find-the-town-judge", "flood-fill"],
        "medium": ["clone-graph", "course-schedule"],
        "hard": ["critical-connections-in-a-network", "reconstruct-itinerary"],
    },
    "linked-list": {
        "easy": ["merge-two-sorted-lists", "linked-list-cycle"],
        "medium": ["remove-nth-node-from-end-of-list", "reorder-list"],
        "hard": ["reverse-nodes-in-k-group"],
    },
    "stack": {
        "easy": ["implement-queue-using-stacks", "backspace-string-compare"],
        "medium": ["evaluate-reverse-polish-notation", "min-stack"],
        "hard": ["basic-calculator", "maximal-rectangle"],
    },
    "greedy": {
        "easy": ["lemonade-change", "can-place-flowers"],
        "medium": ["gas-station", "partition-labels"],
        "hard": ["ipo", "minimum-number-of-refueling-stops"],
    },
    "backtracking": {
        "easy": ["binary-tree-paths", "sum-of-all-subset-xor-totals"],
        "medium": ["permutations", "combination-sum", "generate-parentheses"],
        "hard": ["sudoku-solver", "word-search-ii"],
    },
    "sorting": {
        "easy": ["squares-of-a-sorted-array", "relative-sort-array"],
        "medium": ["merge-intervals", "kth-largest-element-in-an-array"],
        "hard": ["maximum-gap", "reverse-pairs"],
    },
    "string": {
        "easy": ["longest-common-prefix", "reverse-string"],
        "medium": ["longest-palindromic-substring", "decode-string"],
        "hard": ["regular-expression-matching", "shortest-palindrome"],
    },
    "heap-priority-queue": {
        "easy": ["kth-largest-element-in-a-stream", "relative-ranks"],
        "medium": ["kth-largest-element-in-an-array", "task-scheduler"],
        "hard": ["sliding-window-maximum", "ipo"],
    },
    "sliding-window": {
        "easy": ["contains-duplicate-ii", "minimum-difference-between-highest-and-lowest-of-k-scores"],
        "medium": ["longest-repeating-character-replacement", "minimum-size-subarray-sum", "permutation-in-string"],
        "hard": ["sliding-window-maximum", "subarrays-with-k-different-integers"],
    },
}


def extend_fallback(fallback: dict) -> None:
    """Add the extra problems to the fallback bank in place, skipping duplicates by slug."""
    known = {p["slug"]: p for topic in fallback.values() for entries in topic.values() for p in entries}
    known.update({slug: p for slug, p in EXTRA_PROBLEMS.items() if slug not in known})
    for topic, by_difficulty in EXTRA_BY_TOPIC.items():
        for difficulty, slugs in by_difficulty.items():
            bucket = fallback.setdefault(topic, {}).setdefault(difficulty, [])
            present = {p["slug"] for p in bucket}
            for slug in slugs:
                if slug in known and slug not in present:
                    bucket.append(known[slug])
                    present.add(slug)
